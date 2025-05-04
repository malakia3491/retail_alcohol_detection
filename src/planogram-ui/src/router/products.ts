import AddProductImagesView from '@/views/Product/AddProductImagesView.vue';

export const productsRoutes = [
  { path: '/products/add-images', name: 'ProductsAddImages', component: AddProductImagesView, meta: { requiresAuth: true } },
];