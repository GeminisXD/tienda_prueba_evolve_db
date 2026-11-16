import { useEffect, useState } from 'react';
import { LogOut, ShoppingCart, Store, User as UserIcon } from 'lucide-react';
import api, { errorMessage } from './api/client';
import type { Product } from './types';
import { useStore } from './context/StoreContext';
import ProductCard from './components/ProductCard';
import CartDrawer from './components/CartDrawer';
import AuthModal from './components/AuthModal';

type Banner = { kind: 'success' | 'error' | 'info'; text: string } | null;

export default function App() {
  const { user, logout, cartCount, clearCart } = useStore();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cartOpen, setCartOpen] = useState(false);
  const [authOpen, setAuthOpen] = useState(false);
  const [banner, setBanner] = useState<Banner>(null);

  useEffect(() => {
    api
      .get<Product[]>('/products/')
      .then((res) => setProducts(res.data))
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const checkout = params.get('checkout');
    const sessionId = params.get('session_id');
    if (!checkout) return;
    window.history.replaceState({}, '', window.location.pathname);
    if (checkout === 'cancel') {
      setBanner({ kind: 'info', text: 'Pago cancelado. Tu carrito sigue guardado.' });
      return;
    }
    if (!sessionId) return;
    api
      .post<{ status: string }>(`/orders/confirm/${sessionId}`)
      .then((res) => {
        if (res.data.status === 'paid') {
          clearCart();
          setBanner({ kind: 'success', text: 'Pago completado. Gracias por tu compra.' });
          return api.get<Product[]>('/products/').then((r) => setProducts(r.data));
        }
        setBanner({ kind: 'info', text: 'El pago aún no se ha confirmado.' });
      })
      .catch((err) => setBanner({ kind: 'error', text: errorMessage(err) }));
  }, [clearCart]);

  const bannerStyles = {
    success: 'bg-green-100 text-green-800',
    error: 'bg-red-100 text-red-800',
    info: 'bg-amber-100 text-amber-800',
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <div className="flex items-center gap-2 text-xl font-bold text-slate-900">
            <Store className="text-indigo-600" /> Evolve Store
          </div>
          <div className="flex items-center gap-3">
            {user ? (
              <>
                <span className="hidden text-sm text-slate-600 sm:inline">{user.email}</span>
                <button
                  onClick={logout}
                  aria-label="Cerrar sesión"
                  className="rounded-xl p-2 text-slate-500 hover:bg-slate-100"
                >
                  <LogOut size={20} />
                </button>
              </>
            ) : (
              <button
                onClick={() => setAuthOpen(true)}
                className="flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
              >
                <UserIcon size={18} /> Entrar
              </button>
            )}
            <button
              onClick={() => setCartOpen(true)}
              aria-label="Abrir carrito"
              className="relative rounded-xl bg-indigo-600 p-2 text-white hover:bg-indigo-700"
            >
              <ShoppingCart size={20} />
              {cartCount > 0 && (
                <span className="absolute -right-2 -top-2 flex h-5 min-w-5 items-center justify-center rounded-full bg-rose-500 px-1 text-xs font-bold">
                  {cartCount}
                </span>
              )}
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-10">
        {banner && (
          <div className={`mb-6 flex items-center justify-between rounded-xl px-4 py-3 text-sm font-medium ${bannerStyles[banner.kind]}`}>
            {banner.text}
            <button onClick={() => setBanner(null)} className="ml-4 underline">
              Cerrar
            </button>
          </div>
        )}
        <h1 className="mb-8 text-3xl font-bold text-slate-900">Catálogo</h1>
        {loading && <p className="text-slate-500">Cargando productos...</p>}
        {error && <p className="text-red-600">{error}</p>}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {products.map((p) => (
            <ProductCard key={p.id} product={p} />
          ))}
        </div>
      </main>

      {cartOpen && (
        <CartDrawer
          onClose={() => setCartOpen(false)}
          onNeedLogin={() => {
            setCartOpen(false);
            setAuthOpen(true);
          }}
        />
      )}
      {authOpen && <AuthModal onClose={() => setAuthOpen(false)} />}
    </div>
  );
}
