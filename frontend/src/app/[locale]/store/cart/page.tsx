'use client';

import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import { useCart } from '@/context/CartContext';
import { Trash2, ShoppingBag, ArrowLeft } from 'lucide-react';

function formatPrice(amount: number, currency = 'TRY'): string {
  return new Intl.NumberFormat('tr-TR', { style: 'currency', currency }).format(amount);
}

export default function CartPage() {
  const t = useTranslations();
  const { items, removeItem, clearCart, total } = useCart();

  if (items.length === 0) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <ShoppingBag className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">{t('store.cart')} bos</h2>
        <p className="text-gray-500 mb-6">Henuz sepetinize urun eklemediniz.</p>
        <Link
          href="/store"
          className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <ArrowLeft className="w-4 h-4" /> {t('store.title')}
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t('store.cart')}</h1>
        <button
          onClick={clearCart}
          className="text-sm text-red-500 hover:text-red-600"
        >
          Sepeti Temizle
        </button>
      </div>

      <div className="space-y-4 mb-8">
        {items.map((item) => {
          const priceField = `price_${item.license_type}` as keyof typeof item.product;
          const price = item.product[priceField] ? parseFloat(item.product[priceField] as string) : 0;

          return (
            <div key={item.product.id} className="bg-white rounded-xl border border-gray-200 p-4 flex items-center gap-4">
              <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                {item.product.featured_image ? (
                  <img src={item.product.featured_image} alt="" className="w-full h-full object-cover rounded-lg" />
                ) : (
                  <ShoppingBag className="w-6 h-6 text-gray-300" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-medium text-gray-900">{item.product.name}</h3>
                <p className="text-xs text-gray-400">
                  {item.license_type === 'monthly'
                    ? t('store.monthly')
                    : item.license_type === 'yearly'
                    ? t('store.yearly')
                    : t('store.oneTime')}
                </p>
              </div>
              <div className="text-right">
                <div className="text-sm font-semibold text-gray-900">
                  {formatPrice(price * item.quantity)}
                </div>
                <button
                  onClick={() => removeItem(item.product.id)}
                  className="text-red-400 hover:text-red-600 mt-1"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center justify-between text-lg font-bold text-gray-900 mb-6">
          <span>{t('common.total')}</span>
          <span>{formatPrice(total)}</span>
        </div>
        <button className="w-full py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition">
          {t('store.checkout')}
        </button>
        <p className="text-xs text-gray-400 text-center mt-3">
          Odeme iyzico guvenli odeme altyapisi ile gerceklestirilir.
        </p>
      </div>
    </div>
  );
}
