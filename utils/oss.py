import oss2
from datetime import datetime
import os
from typing import BinaryIO
from fastapi import HTTPException

class OSSClient:
    def __init__(self):
        self.access_key_id = os.getenv('ALI_AK')
        self.access_key_secret = os.getenv('ALI_SK')
        self.endpoint = os.getenv('ALI_OSS_ENDPOINT')
        self.bucket_name = os.getenv('ALI_OSS_BUCKET_NAME')
        
        if not all([self.access_key_id, self.access_key_secret, self.endpoint, self.bucket_name]):
            raise ValueError("Missing OSS configuration")
        
        self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucket_name)
    
    def upload_file(self, file_content: BinaryIO, filename: str) -> str:
        """上传文件到OSS并返回URL"""
        try:
            # 生成OSS中的文件路径：recordings/年月日/文件名
            date_prefix = datetime.now().strftime('%Y%m%d')
            oss_path = f"recordings/{date_prefix}/{filename}"
            
            # 上传文件
            self.bucket.put_object(oss_path, file_content)
            
            # 生成文件URL（默认有效期为3600秒）
            url = self.bucket.sign_url('GET', oss_path, 3600)
            return url
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file to OSS: {str(e)}"
            ) 