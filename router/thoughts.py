import io
import logging
from typing import Dict, Any, List

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from mutagen import File as MutagenFile
from sqlmodel import Session

from utils.database import get_db
from models.thoughts import Recording
from packages.fastapi.standard_error import standard_error_handler
from router.oss import upload_file_to_oss

thoughts_router = APIRouter(prefix='/thoughts', tags=['thoughts'])
logger = logging.getLogger(__name__)

# 设置最大文件大小
MAX_FILE_SIZE = 10 * 1024 * 1024  # N MB in bytes


@thoughts_router.post("/new")
@standard_error_handler()
async def get_record_metadata(
    upload_file: UploadFile = File(..., description="iOS Shortcuts录音文件"), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取录音文件的元数据信息，并保存到OSS和数据库
    """
    try:
        # 读取文件内容到内存
        content = await upload_file.read()

        # 检查文件大小
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400,
                                detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE / 1024 / 1024}MB")

        # 使用BytesIO创建一个内存文件对象用于mutagen分析
        file = io.BytesIO(content)
        audio = MutagenFile(file)

        if audio is None:
            raise HTTPException(status_code=400, detail="Unsupported audio format or corrupted file")

        # 准备元数据 - 使用 upload_file 而不是 file 来获取文件名
        metadata = {
            "filename": upload_file.filename,
            "content_type": upload_file.content_type,
            "file_size": len(content),
            "tags": {}
        }

        # 添加音频特定的元数据
        try:
            if hasattr(audio.info, "length"):
                metadata["duration"] = round(audio.info.length, 2)
            if hasattr(audio.info, "bitrate"):
                metadata["bitrate"] = audio.info.bitrate
            if hasattr(audio.info, "sample_rate"):
                metadata["sample_rate"] = audio.info.sample_rate

            # 获取音频格式
            if hasattr(audio, 'mime') and audio.mime:
                try:
                    metadata["audio_format"] = audio.mime[0].split("/")[1]
                except (AttributeError, IndexError):
                    metadata["audio_format"] = None
            else:
                metadata["audio_format"] = upload_file.filename.split('.')[-1]

            # 获取标签信息
            if hasattr(audio, "tags") and audio.tags:
                try:
                    metadata["tags"] = dict(audio.tags)
                except Exception as e:
                    logger.warning(f"Failed to extract tags: {str(e)}")

        except Exception as e:
            logger.error(f"Error extracting audio metadata: {str(e)}")
            metadata["error_details"] = str(e)

        # 上传到OSS - 使用原始的 upload_file
        await upload_file.seek(0)  # 重置文件指针到开始
        oss_url = upload_file_to_oss(upload_file, upload_file.filename)

        # 创建数据库记录
        db_recording = Recording(filename=metadata["filename"],
                                 content_type=metadata["content_type"],
                                 file_size=metadata["file_size"],
                                 oss_url=oss_url,
                                 duration=metadata.get("duration"),
                                 bitrate=metadata.get("bitrate"),
                                 sample_rate=metadata.get("sample_rate"),
                                 audio_format=metadata.get("audio_format"),
                                 metadata=metadata.get("tags", {}))

        db.add(db_recording)
        db.commit()
        db.refresh(db_recording)

        return metadata

    except Exception as e:
        logger.error(f"Failed to process audio file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process audio file: {str(e)}")


@thoughts_router.get("/list", response_model=List[Dict[str, Any]])
@standard_error_handler()
async def list_records(
    skip: int = Query(default=0, ge=0), limit: int = Query(default=10, ge=1, le=100), db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    获取已上传的录音文件列表（分页）
    
    Args:
        skip: 跳过的记录数
        limit: 返回的最大记录数
        db: 数据库会话
    """
    try:
        recordings = db.query(Recording).order_by(Recording.created_at.desc()).offset(skip).limit(limit).all()

        return [{
            "id": record.id,
            "filename": record.filename,
            "file_size": record.file_size,
            "duration": record.duration,
            "bitrate": record.bitrate,
            "created_time": record.created_at.isoformat(),
            "modified_time": record.updated_at.isoformat(),
            "audio_format": record.audio_format,
            "metadata": record.meta,
            "url": record.oss_url} for record in recordings]

    except Exception as e:
        logger.error(f"Failed to list records: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list records: {str(e)}")
