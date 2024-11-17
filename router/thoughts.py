from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any, List
from mutagen import File as MutagenFile
import os
from datetime import datetime
import logging

from packages.fastapi.standard_error import standard_error_handler

thoughts_router = APIRouter(prefix='/thoughts', tags=['thoughts'])
logger = logging.getLogger(__name__)

# 添加录音文件存储路径的常量
RECORDINGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recordings")
os.makedirs(RECORDINGS_DIR, exist_ok=True)

@thoughts_router.post("/new")
@standard_error_handler()
async def get_record_metadata(
    record: UploadFile = File(..., description="iOS Shortcuts录音文件")
) -> Dict[str, Any]:
    """
    获取录音文件的元数据信息，并保存文件
    
    Args:
        record (UploadFile): iOS Shortcuts录制的音频文件
        
    Returns:
        Dict[str, Any]: 包含文件元数据的字典
    """
    temp_path = None
    try:
        # 保存上传的文件到临时位置
        temp_path = f"/tmp/{record.filename}"
        with open(temp_path, "wb") as buffer:
            content = await record.read()
            buffer.write(content)
        
        # 使用mutagen读取文件元数据
        audio = MutagenFile(temp_path)
        if audio is None:
            raise HTTPException(status_code=400, detail="Unsupported audio format or corrupted file")
        
        # 获取文件基本信息
        file_stats = os.stat(temp_path)
        
        metadata = {
            "filename": record.filename,
            "content_type": record.content_type,
            "file_size": file_stats.st_size,
            "created_time": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            "modified_time": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
        }
        
        # 添加音频特定的元数据
        try:
            if hasattr(audio.info, "length"):
                metadata["duration"] = round(audio.info.length, 2)
            if hasattr(audio.info, "bitrate"):
                metadata["bitrate"] = audio.info.bitrate
            if hasattr(audio.info, "sample_rate"):
                metadata["sample_rate"] = audio.info.sample_rate
            
            # 安全地获取音频格式
            if hasattr(audio, 'mime') and audio.mime:
                try:
                    metadata["audio_format"] = audio.mime[0].split("/")[1]
                except (AttributeError, IndexError):
                    metadata["audio_format"] = None
            else:
                # 尝试从文件扩展名获取格式
                metadata["audio_format"] = os.path.splitext(record.filename)[1].lstrip('.')
            
            # 安全地获取标签信息
            if hasattr(audio, "tags") and audio.tags:
                try:
                    metadata["tags"] = dict(audio.tags)
                except Exception as e:
                    logger.warning(f"Failed to extract tags: {str(e)}")
                    metadata["tags"] = {}
            
        except Exception as e:
            logger.error(f"Error extracting audio metadata: {str(e)}")
            metadata["error_details"] = str(e)
        
        # 将文件从临时目录移动到永久存储位置
        permanent_path = os.path.join(RECORDINGS_DIR, record.filename)
        try:
            os.rename(temp_path, permanent_path)
            temp_path = None  # 防止finally块中删除已移动的文件
            logger.info(f"Successfully saved recording to {permanent_path}")
        except Exception as e:
            logger.error(f"Failed to save recording: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to save recording file"
            )
        
        return metadata

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Failed to process audio file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process audio file: {str(e)}"
        )
    finally:
        # 确保清理临时文件（如果还存在的话）
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                logger.error(f"Failed to remove temp file {temp_path}: {str(e)}")

@thoughts_router.get("/list", response_model=List[Dict[str, Any]])
@standard_error_handler()
async def list_records() -> List[Dict[str, Any]]:
    """
    获取所有已上传的录音文件列表
    
    Returns:
        List[Dict[str, Any]]: 包含所有录音文件信息的列表
    """
    try:
        records = []
        for filename in os.listdir(RECORDINGS_DIR):
            file_path = os.path.join(RECORDINGS_DIR, filename)
            if os.path.isfile(file_path):
                file_stats = os.stat(file_path)
                
                # 基本文件信息
                record_info = {
                    "filename": filename,
                    "file_size": file_stats.st_size,
                    "created_time": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                    "modified_time": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                }
                
                # 尝试获取音频文件的元数据
                try:
                    audio = MutagenFile(file_path)
                    if audio and hasattr(audio.info, "length"):
                        record_info["duration"] = round(audio.info.length, 2)
                    if audio and hasattr(audio.info, "bitrate"):
                        record_info["bitrate"] = audio.info.bitrate
                except Exception as e:
                    logger.warning(f"Failed to read metadata for {filename}: {str(e)}")
                
                records.append(record_info)
        
        # 按修改时间降序排序
        records.sort(key=lambda x: x["modified_time"], reverse=True)
        return records
        
    except Exception as e:
        logger.error(f"Failed to list records: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list records: {str(e)}"
        )
