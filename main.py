from fastapi import FastAPI, HTTPException, status, Request
from typing import List
from models import User, UserUpdate
from uuid import UUID, uuid4
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime, timedelta

app = FastAPI()

db: List[User] = [
	User(
		# u_id = uuid4(),
        u_id = UUID('a5f5b8b8-458e-42bb-af73-65e11cb321d1'),
		account = 'sandy',
		password = 'Sandy123'
	),
]

# Find All Users
@app.get('/users', status_code=200)
async def users_get_all():
    return db;

# Find one user
@app.get('/users/{u_id}', status_code=200)
async def users_get_one(u_id: UUID):
    for user in db:
        if user.u_id == u_id:
            return {'Success': True}
    # Raise Error when the user is not in the DB
    raise HTTPException(status_code=404, detail=f'User with id "{u_id}" does not exist!')
    

# Add a user
@app.post('/users', status_code=201)
async def user_create(user:User):  # User comes from POST Request Body we gave
    for current_user in db:
        if user.account == current_user.account:
            raise HTTPException(status_code=400, detail=f'The account is already in use.')
    db.append(user)
    return {"Success" : True}

# # Modify a user
@app.put('/users/{u_id}', status_code=204)
async def user_update(new_user: UserUpdate, u_id: UUID):
    for current_user in db:
        if new_user.account == current_user.account:
            raise HTTPException(status_code=400, detail=f'The account is already in use.')
    for current_user in db:
        if current_user.u_id == u_id:
            if current_user.account is not None:
                current_user.account = new_user.account
            if current_user.password is not None:
                current_user.password = new_user.password

            return
    # Raise Error when the user is not in the DB 
    raise HTTPException(
		status_code=404,
  		detail=f'User with id "{u_id}" does not exist!'	
	)
                

# # Delete a user
@app.delete('/users/{u_id}', status_code=204)
async def user_delete(u_id: UUID):
    for user in db:
        if user.u_id == u_id:
            db.remove(user)
            return
    # Raise Error when the user is not in the DB
    raise HTTPException(
        status_code=404,
        detail=f'User with id "{u_id}" does not exist!'
    )

attempts = 0
now_plus_1_min = None

@app.post('/auth', status_code=200)
async def auth(user:User):
    global attempts
    global now_plus_1_min
    for data in db:
        if data.account == user.account:
            while attempts < 5:
                if data.password == user.password:
                    return {'Success': True}
                attempts += 1
                raise HTTPException(status_code=401, detail='Wrong password')
            
            # Fail for 5 times -> wait for 1 min 
            wait_for_one_min()

        raise HTTPException(status_code=401, detail='Wrong account')


def wait_for_one_min():
    global attempts
    global now_plus_1_min
    
    now = datetime.now()
    
    if not now_plus_1_min:
        now_plus_1_min = now + timedelta(minutes = 1)
        
    if now >= now_plus_1_min:
        attempts = 1
        now_plus_1_min = None
        return
    else:
        time_to_wait = round((now_plus_1_min-now).total_seconds())
        raise HTTPException(
            status_code=429,
            detail='You failed too many times, Please wait {} sec to retry.'.format(time_to_wait)
        )
    

# Override HTTPException
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            {
                "Success": False,
                "Reason": exc.detail,
            }
        ),
    )

# Override the Request Validation Exceptions
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            {
                "Success": False,
                "Reason": exc._errors[0]["msg"],
            }
        ),
    )