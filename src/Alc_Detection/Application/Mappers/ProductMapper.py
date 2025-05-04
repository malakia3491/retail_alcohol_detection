from Alc_Detection.Domain.Store.Product import Product
from Alc_Detection.Domain.NetworkModels.Embedding import Embedding
from Alc_Detection.Domain.NetworkModels.Image import Image
from Alc_Detection.Domain.NetworkModels.EmbeddingModel import EmbeddingNetwork
from Alc_Detection.Application.Requests.Models import Product as ProductResponseModel
from Alc_Detection.Persistance.Models.Models import Product as ProductModel 
from Alc_Detection.Persistance.Models.Models import Embedding as EmbeddingModel
from Alc_Detection.Persistance.Models.Models import EmbeddingModel as EmbeddingModelModel
from Alc_Detection.Persistance.Models.Models import ProductImage as ProductImageModel

class ProductMapper:
        
    def map_to_domain_model(self,
                            db_model: ProductModel,
    ) -> Product:
        if db_model is None: return None
        if not isinstance(db_model, ProductModel):
            raise ValueError(db_model)
        images = []
        
        for db_img in db_model.images:
            embeddings = []
            for emb in db_img.embeddings:
                model = EmbeddingNetwork(id=emb.model.id,
                                         path=emb.model.path,
                                         embedding_shape=emb.model.embedding_shape,
                                         version=emb.model.version)    
                embeddings.append(Embedding(id=emb.id,
                                            cords=list(emb.vector),
                                            model=model))                            
            img = Image(path=db_img.path,
                        embeddings=embeddings)
            images.append(img)
        return Product(id=db_model.id,
                       label=db_model.label,
                       images=images,
                       name=db_model.name)        
    
    def map_to_db_model(self,
                        domain_model: Product
    ) -> ProductModel:
        if domain_model is None: return None
        if not isinstance(domain_model, Product):
            raise ValueError(domain_model)
        
        return ProductModel(id=domain_model.id,
                            name=domain_model.name)  
        
    def map_to_response_model(self,
                              domain_model: Product
    ) -> ProductResponseModel:
        if domain_model is None: return None
        if not isinstance(domain_model, Product):
            raise ValueError(domain_model)
        
        return ProductResponseModel(id=domain_model.id,
                                    image_url=f"/static/products/{domain_model.id}/{domain_model.image.name}",
                                    name=domain_model.name)