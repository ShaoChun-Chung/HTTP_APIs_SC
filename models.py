from typing import Optional, List
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, ImportString, field_validator, Field
from enum import Enum

def len_constraints_account(cls, value):
    if len(value) < 3:
            print(len(value))
            raise ValueError('The minimum length for account is 3.')
    elif len(value) > 32:
            raise ValueError('The maximum length for account is 32.')
    return value

def len_constraints_password(cls, value):
        if len(value) < 8:
            raise ValueError('The minimum length for password is 8.')
        elif len(value) > 32:
            raise ValueError('The maximum length for password is 32.')
        return value

def contain_constraints_password(cls, value):
    if not any(c.isupper() for c in value):
        raise ValueError('Your password must contain at least 1 uppercase letter.')
    if not any(c.islower() for c in value):
        raise ValueError('Your password must contain at least 1 lowercase letter.')
    if not any(c.isdigit() for c in value):
        raise ValueError('Your password must contain at least 1 number.') 
    return value 
 

class User(BaseModel):
    u_id: Optional[UUID] = uuid4()
    account: str 
    password: str
    
    normalized_account = field_validator('account')(len_constraints_account)
    
    password = field_validator('password')(len_constraints_password)
    normalized_password = field_validator('password')(contain_constraints_password)
    
    
class UserUpdate(BaseModel):
    account: Optional[str]
    password: Optional[str]
    
    normalized_account = field_validator('account')(len_constraints_account)
    
    password = field_validator('password')(len_constraints_password)
    normalized_password = field_validator('password')(contain_constraints_password)