from Alc_Detection.Domain.Store.PersonManagment.Permition import Permition
from Alc_Detection.Domain.Store.PersonManagment.Post import Post
from Alc_Detection.Persistance.Models.Models import Post as PostModel
from Alc_Detection.Persistance.Models.Models import PostPermition as PostPermitionModel

class PostMapper:
    def map_to_domain_model(self, db_model: PostModel) -> Post:
        if db_model is None: return None
        if not isinstance(db_model, PostModel):
            raise ValueError(db_model)

        permitions: list[Permition] = []
        for post_permition_db in db_model.post_permitions:
            permition = Permition(
                id=post_permition_db.permition.id,
                name=post_permition_db.permition.name
            )
            permitions.append(permition)
        return Post(id=db_model.id,
                    retail_id=db_model.retail_id,
                    name=db_model.name,
                    permitions=permitions)
        
    def map_to_db_model(self, domain_model: Post) -> PostModel:
        if domain_model is None: return None
        if not isinstance(domain_model, Post):
            raise ValueError(domain_model)
        
        permitions_db: list[PostPermitionModel] = []
        for permition in domain_model.permitions:
            permition_db = PostPermitionModel(
                permition_id=permition.id
            )
            permitions_db.append(permition_db)
        
        return PostModel(
            retail_id=domain_model.retail_id,
            name=domain_model.name,
            post_permitions=permitions_db
        )