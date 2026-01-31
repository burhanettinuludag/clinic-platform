'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';
import { useProducts, useProductCategories } from '@/hooks/useStoreData';
import { useCart } from '@/context/CartContext';
import { ShoppingCart, Package, Star } from 'lucide-react';
import type { Product, LicenseType } from '@/lib/types/store';

function formatPrice(amount: string | null, currency: string): string {
  if (!amount) return '-';
  const num = parseFloat(amount);
  return new Intl.NumberFormat('tr-TR', { style: 'currency', currency }).format(num);
}

function getLowestPrice(product: Product): { price: string | null; type: LicenseType } {
  const prices: { price: string | null; type: LicenseType }[] = [
    { price: product.price_monthly, type: 'monthly' },
    { price: product.price_yearly, type: 'yearly' },
    { price: product.price_one_time, type: 'one_time' },
  ];
  const valid = prices.filter((p) => p.price && parseFloat(p.price) > 0);
  if (valid.length === 0) return { price: null, type: 'one_time' };
  valid.sort((a, b) => parseFloat(a.price!) - parseFloat(b.price!));
  return valid[0];
}

export default function StorePage() {
  const t = useTranslations();
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>();
  const { data: products, isLoading } = useProducts(
    selectedCategory ? { category: selectedCategory } : undefined
  );
  const { data: categories } = useProductCategories();
  const { addItem, itemCount } = useCart();

  const handleAddToCart = (product: Product) => {
    const { type } = getLowestPrice(product);
    addItem(product, type);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('store.title')}</h1>
          <p className="text-gray-500 mt-1">Gelistirdigimiz dijital saglik yazilimlari ve araclari.</p>
        </div>
        <Link
          href="/store/cart"
          className="relative flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <ShoppingCart className="w-5 h-5" />
          {t('store.cart')}
          {itemCount > 0 && (
            <span className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
              {itemCount}
            </span>
          )}
        </Link>
      </div>

      {/* Categories */}
      {categories && categories.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-8">
          <button
            onClick={() => setSelectedCategory(undefined)}
            className={`px-4 py-2 rounded-full text-sm transition ${
              !selectedCategory ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {t('common.total')}
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-4 py-2 rounded-full text-sm transition ${
                selectedCategory === cat.id ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>
      )}

      {/* Products Grid */}
      {isLoading ? (
        <div className="text-center py-12 text-gray-500">{t('common.loading')}</div>
      ) : products && products.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product) => {
            const lowest = getLowestPrice(product);
            return (
              <div key={product.id} className="bg-white rounded-xl border border-gray-200 overflow-hidden group hover:shadow-lg transition">
                {product.featured_image ? (
                  <div className="aspect-video bg-gray-100 overflow-hidden">
                    <img
                      src={product.featured_image}
                      alt={product.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition"
                    />
                  </div>
                ) : (
                  <div className="aspect-video bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
                    <Package className="w-12 h-12 text-gray-300" />
                  </div>
                )}
                <div className="p-5">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      {product.is_featured && (
                        <span className="inline-flex items-center gap-1 text-xs text-yellow-600 mb-1">
                          <Star className="w-3 h-3" /> One Cikan
                        </span>
                      )}
                      <h2 className="text-lg font-semibold text-gray-900">{product.name}</h2>
                    </div>
                    {product.version && (
                      <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded">
                        v{product.version}
                      </span>
                    )}
                  </div>
                  {product.short_description && (
                    <p className="text-sm text-gray-500 line-clamp-2 mb-4">{product.short_description}</p>
                  )}
                  <div className="flex items-center justify-between">
                    <div>
                      {lowest.price && (
                        <span className="text-lg font-bold text-gray-900">
                          {formatPrice(lowest.price, product.currency)}
                        </span>
                      )}
                      {lowest.type !== 'one_time' && (
                        <span className="text-xs text-gray-400 ml-1">
                          /{t(`store.${lowest.type === 'monthly' ? 'monthly' : 'yearly'}`).toLowerCase()}
                        </span>
                      )}
                    </div>
                    <button
                      onClick={() => handleAddToCart(product)}
                      className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition"
                    >
                      {t('store.addToCart')}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">{t('common.noResults')}</div>
      )}
    </div>
  );
}
