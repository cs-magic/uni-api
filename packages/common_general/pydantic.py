from datetime import datetime, date

from pydantic import BaseModel as PydanticBaseMode


class BaseModel(PydanticBaseMode):
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S'),
            date: lambda v: v.strftime('%Y-%m-%d'),
        }
    
    def dict(self, *args, **kwargs):
        # Get the standard dictionary representation of the model
        model_dict = super().dict(*args, **kwargs)
        
        # Customize the serialization of date and datetime fields
        for field, value in model_dict.items():
            if isinstance(value, date):  # This includes datetime since datetime is a subclass of date
                # Convert date/datetime to a string in a custom format
                model_dict[field] = value.strftime('%Y-%m-%d %H:%M:%S' if isinstance(value, datetime) else '%d-%m-%Y')
        return model_dict
