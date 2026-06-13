import api from './client';
import type { Product } from './products-api';

export interface OrderItemRequest {
  product_id: number;
  quantity: number;
}

export interface OrderCreateRequest {
  customer_name: string;
  phone: string;
  address: string;
  comment?: string;
  items: OrderItemRequest[];
}

export async function createOrder(orderData: OrderCreateRequest) {
  const response = await api.post('/orders/', orderData);
  return response.data;
}
