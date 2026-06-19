import api from './client';

export interface WalletBalance {
  telegram_id: number;
  balance: number;
}

export interface TopUpResponse {
  payment_id: string;
  confirmation_url: string;
}

export async function getWalletBalance(): Promise<WalletBalance> {
  const response = await api.get<WalletBalance>('/wallet/balance');
  return response.data;
}

export async function topUpWallet(amount: number): Promise<TopUpResponse> {
  const response = await api.post<TopUpResponse>(`/wallet/top-up?amount=${amount}`);
  return response.data;
}

export async function mockPaymentSuccess(paymentId: string): Promise<void> {
  await api.post(`/wallet/mock-success/${paymentId}`);
}

export async function payOrderFromWallet(orderId: number): Promise<{ success: boolean; message: string; new_balance: number }> {
  const response = await api.post(`/orders/${orderId}/pay`);
  return response.data;
}