import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import api from '../api/client';
import type { CartLine, Product, User } from '../types';

interface StoreValue {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  cart: CartLine[];
  cartCount: number;
  cartTotal: number;
  addToCart: (product: Product) => void;
  setQuantity: (productId: number, quantity: number) => void;
  removeFromCart: (productId: number) => void;
  clearCart: () => void;
}

const StoreContext = createContext<StoreValue | null>(null);

function loadCart(): CartLine[] {
  try {
    return JSON.parse(localStorage.getItem('cart') ?? '[]');
  } catch {
    return [];
  }
}

export function StoreProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [cart, setCart] = useState<CartLine[]>(loadCart);

  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cart));
  }, [cart]);

  useEffect(() => {
    if (!localStorage.getItem('token')) return;
    api
      .get<User>('/auth/me')
      .then((res) => setUser(res.data))
      .catch(() => localStorage.removeItem('token'));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const body = new URLSearchParams({ username: email, password });
    const res = await api.post<{ access_token: string }>('/auth/login', body);
    localStorage.setItem('token', res.data.access_token);
    const me = await api.get<User>('/auth/me');
    setUser(me.data);
  }, []);

  const register = useCallback(
    async (email: string, password: string) => {
      await api.post('/auth/register', { email, password });
      await login(email, password);
    },
    [login],
  );

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setUser(null);
  }, []);

  const addToCart = useCallback((product: Product) => {
    setCart((prev) => {
      const line = prev.find((l) => l.product.id === product.id);
      if (!line) return product.stock > 0 ? [...prev, { product, quantity: 1 }] : prev;
      return prev.map((l) =>
        l.product.id === product.id
          ? { ...l, product, quantity: Math.min(l.quantity + 1, product.stock) }
          : l,
      );
    });
  }, []);

  const setQuantity = useCallback((productId: number, quantity: number) => {
    setCart((prev) =>
      prev
        .map((l) =>
          l.product.id === productId
            ? { ...l, quantity: Math.min(quantity, l.product.stock) }
            : l,
        )
        .filter((l) => l.quantity > 0),
    );
  }, []);

  const removeFromCart = useCallback((productId: number) => {
    setCart((prev) => prev.filter((l) => l.product.id !== productId));
  }, []);

  const clearCart = useCallback(() => setCart([]), []);

  const value = useMemo<StoreValue>(
    () => ({
      user,
      login,
      register,
      logout,
      cart,
      cartCount: cart.reduce((n, l) => n + l.quantity, 0),
      cartTotal: cart.reduce((n, l) => n + l.quantity * l.product.price, 0),
      addToCart,
      setQuantity,
      removeFromCart,
      clearCart,
    }),
    [user, login, register, logout, cart, addToCart, setQuantity, removeFromCart, clearCart],
  );

  return <StoreContext.Provider value={value}>{children}</StoreContext.Provider>;
}

export function useStore(): StoreValue {
  const ctx = useContext(StoreContext);
  if (!ctx) throw new Error('useStore debe usarse dentro de StoreProvider');
  return ctx;
}
