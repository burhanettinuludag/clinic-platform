'use client';

import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import type { Product, CartItem, LicenseType } from '@/lib/types/store';

interface CartContextType {
  items: CartItem[];
  addItem: (product: Product, licenseType: LicenseType) => void;
  removeItem: (productId: string) => void;
  clearCart: () => void;
  itemCount: number;
  total: number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

function getPrice(product: Product, licenseType: LicenseType): number {
  const priceField = `price_${licenseType}` as keyof Product;
  const price = product[priceField];
  return price ? parseFloat(price as string) : 0;
}

export function CartProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([]);

  const addItem = useCallback((product: Product, licenseType: LicenseType) => {
    setItems((prev) => {
      const existing = prev.find(
        (item) => item.product.id === product.id && item.license_type === licenseType
      );
      if (existing) {
        return prev.map((item) =>
          item.product.id === product.id && item.license_type === licenseType
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prev, { product, license_type: licenseType, quantity: 1 }];
    });
  }, []);

  const removeItem = useCallback((productId: string) => {
    setItems((prev) => prev.filter((item) => item.product.id !== productId));
  }, []);

  const clearCart = useCallback(() => setItems([]), []);

  const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);
  const total = items.reduce(
    (sum, item) => sum + getPrice(item.product, item.license_type) * item.quantity,
    0
  );

  return (
    <CartContext.Provider value={{ items, addItem, removeItem, clearCart, itemCount, total }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}
