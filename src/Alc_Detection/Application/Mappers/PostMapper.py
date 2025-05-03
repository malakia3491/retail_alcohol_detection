from Alc_Detection.Domain.Store.PersonManagment.Post import Post
from Alc_Detection.Persistance.Models.Models import Post as PostModel

class PostMapper:
    def map_to_domain_model(self, db_model: PostModel) -> Post:
        if db_model is None: return None
        if not isinstance(db_model, PostModel):
            raise ValueError(db_model)
        return Post(id=db_model.id,
                    name=db_model.name,
                    is_regular=db_model.is_regular,
                    is_administrative=db_model.is_administrative)