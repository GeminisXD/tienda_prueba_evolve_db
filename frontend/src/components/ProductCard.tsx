import { ShoppingCart } from 'lucide-react';
import type { Product } from '../types';
import { useStore } from '../context/StoreContext';
import { formatPrice } from '../format';

export default function ProductCard({ product }: { product: Product }) {
  const { addToCart, cart } = useStore();
  const inCart = cart.find((l) => l.product.id === product.id)?.quantity ?? 0;
  const soldOut = product.stock <= 0;
  const maxed = inCart >= product.stock;

  return (
    <article className="flex flex-col overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200 transition hover:shadow-lg">
      <div className="relative aspect-[4/3] bg-slate-100">
        {product.image_url && (
          <img src={product.image_url} alt={product.name} loading="lazy" className="h-full w-full object-cover" />
        )}
        {soldOut && (
          <span className="absolute left-3 top-3 rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold text-white">
            Agotado
          </span>
        )}
        {!soldOut && product.stock <= 5 && (
          <span className="absolute left-3 top-3 rounded-full bg-amber-500 px-3 py-1 text-xs font-semibold text-white">
            Quedan {product.stock}
          </span>
        )}
      </div>
      <div className="flex flex-1 flex-col gap-2 p-5">
        <h2 className="text-lg font-semibold text-slate-900">{product.name}</h2>
        <p className="line-clamp-2 flex-1 text-sm text-slate-500">{product.description}</p>
        <div className="mt-2 flex items-center justify-between">
          <span className="text-xl font-bold text-indigo-600">{formatPrice(product.price)}</span>
          <button
            onClick={() => addToCart(product)}
            disabled={soldOut || maxed}
            className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            <ShoppingCart size={16} />
            {inCart > 0 ? `Añadido (${inCart})` : 'Añadir'}
          </button>
        </div>
      </div>
    </article>
  );
}
