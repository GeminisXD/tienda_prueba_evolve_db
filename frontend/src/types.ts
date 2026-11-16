export interface Product {
  id: number;
  name: string;
  description: string | null;
  price: number;
  stock: number;
  image_url: string | null;
}

export interface User {
  id: number;
  email: string;
}

export interface CartLine {
  product: Product;
  quantity: number;
}
