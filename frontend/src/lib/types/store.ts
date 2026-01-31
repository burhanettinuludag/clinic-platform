export interface ProductCategory {
  id: string;
  slug: string;
  name: string;
  name_tr: string;
  name_en: string;
  description: string;
  order: number;
}

export interface Product {
  id: string;
  slug: string;
  name: string;
  short_description: string;
  description?: string;
  product_type: 'software' | 'tool' | 'template' | 'course';
  category: string | null;
  category_name: string | null;
  featured_image: string;
  screenshots?: string[];
  price_monthly: string | null;
  price_yearly: string | null;
  price_one_time: string | null;
  currency: string;
  is_featured: boolean;
  version: string;
  system_requirements?: string;
}

export type LicenseType = 'monthly' | 'yearly' | 'one_time';

export interface CartItem {
  product: Product;
  license_type: LicenseType;
  quantity: number;
}

export interface OrderItem {
  id: string;
  product: string;
  product_name: string;
  quantity: number;
  unit_price: string;
  license_type: LicenseType;
}

export interface Order {
  id: string;
  order_number: string;
  status: string;
  total_amount: string;
  currency: string;
  billing_name: string;
  billing_address: string;
  billing_city: string;
  billing_country: string;
  billing_zip_code: string;
  items: OrderItem[];
  created_at: string;
  paid_at: string | null;
}

export interface License {
  id: string;
  product: string;
  product_name: string;
  license_key: string;
  license_type: string;
  starts_at: string;
  expires_at: string | null;
  is_active: boolean;
  max_activations: number;
  current_activations: number;
}
