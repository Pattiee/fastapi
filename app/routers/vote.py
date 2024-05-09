from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import schemas, database, models, oath2
from sqlalchemy.orm import Session

router = APIRouter(prefix="/vote", tags=['Votes'])


@router.post('/', status_code=status.HTTP_201_CREATED)
def vote(vote_req: schemas.VoteRequest,
         current_user: int = Depends(oath2.get_current_user),
         db: Session = Depends(database.get_db)):
    post = db.query(models.Post).filter(models.Post.id == vote_req.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {vote_req.post_id} not existing")

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote_req.post_id,
                                              models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()
    if vote_req.dir == 1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"You have already voted on the post!")
        new_vote = models.Vote(user_id=current_user.id, post_id=vote_req.post_id)
        db.add(new_vote)
        db.commit()
        return {"message": "Successfully voted"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Vote does not exist!")

        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Successfully deleted voted"}
