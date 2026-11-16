import { useState } from 'react';
import { Minus, Plus, Trash2, X, CreditCard } from 'lucide-react';
import { useStore } from '../context/StoreContext';
import api, { errorMessage } from '../api/client';
import { formatPrice } from '../format';

interface Props {
  onClose: () => void;
  onNeedLogin: () => void;
}

export default function CartDrawer({ onClose, onNeedLogin }: Props) {
  const { cart, cartTotal, user, setQuantity, removeFromCart } = useStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function checkout() {
    if (!user) {
      onNeedLogin();
      return;
    }
    setError('');
    setLoading(true);
    try {
      const items = cart.map((l) => ({ product_id: l.product.id, quantity: l.quantity }));
      const res = await api.post<{ checkout_url: string }>('/orders/checkout', { items });
      window.location.href = res.data.checkout_url;
    } catch (err) {
      setError(errorMessage(err));
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-40 flex justify-end bg-slate-900/50" onClick={onClose}>
      <aside
        onClick={(e) => e.stopPropagation()}
        className="flex h-full w-full max-w-md flex-col bg-white shadow-2xl"
      >
        <div className="flex items-center justify-between border-b border-slate-200 p-5">
          <h2 className="text-xl font-bold text-slate-900">Tu carrito</h2>
          <button onClick={onClose} aria-label="Cerrar" className="text-slate-400 hover:text-slate-700">
            <X size={22} />
          </button>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto p-5">
          {cart.length === 0 && <p className="mt-10 text-center text-slate-500">El carrito está vacío.</p>}
          {cart.map(({ product, quantity }) => (
            <div key={product.id} className="flex gap-4">
              {product.image_url && (
                <img src={product.image_url} alt={product.name} className="h-20 w-20 rounded-xl object-cover" />
              )}
              <div className="flex-1">
                <p className="font-medium text-slate-900">{product.name}</p>
                <p className="text-sm text-slate-500">{formatPrice(product.price)}</p>
                <div className="mt-2 flex items-center gap-2">
                  <button
                    onClick={() => setQuantity(product.id, quantity - 1)}
                    aria-label="Quitar uno"
                    className="rounded-lg border border-slate-300 p-1 hover:bg-slate-100"
                  >
                    <Minus size={14} />
                  </button>
                  <span className="w-6 text-center text-sm">{quantity}</span>
                  <button
                    onClick={() => setQuantity(product.id, quantity + 1)}
                    disabled={quantity >= product.stock}
                    aria-label="Añadir uno"
                    className="rounded-lg border border-slate-300 p-1 hover:bg-slate-100 disabled:opacity-40"
                  >
                    <Plus size={14} />
                  </button>
                  <button
                    onClick={() => removeFromCart(product.id)}
                    aria-label="Eliminar"
                    className="ml-auto text-slate-400 hover:text-red-600"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="space-y-3 border-t border-slate-200 p-5">
          <div className="flex justify-between text-lg font-semibold text-slate-900">
            <span>Total</span>
            <span>{formatPrice(cartTotal)}</span>
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button
            onClick={checkout}
            disabled={cart.length === 0 || loading}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 py-3 font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            <CreditCard size={18} />
            {loading ? 'Redirigiendo a Stripe...' : user ? 'Pagar con Stripe' : 'Inicia sesión para pagar'}
          </button>
        </div>
      </aside>
    </div>
  );
}
