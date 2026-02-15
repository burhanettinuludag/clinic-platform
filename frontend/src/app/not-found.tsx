import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-slate-900 px-4">
      <div className="text-center">
        <div className="mb-6">
          <span className="text-8xl font-bold bg-gradient-to-r from-cyan-500 to-purple-600 bg-clip-text text-transparent">404</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Sayfa Bulunamadi</h1>
        <p className="text-gray-500 dark:text-gray-400 mb-8 max-w-sm mx-auto">
          Aradiginiz sayfa tasinmis, silinmis veya hic var olmamis olabilir.
        </p>
        <div className="flex items-center justify-center gap-3">
          <Link href="/" className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700 transition-colors">
            Ana Sayfa
          </Link>
          <Link href="/blog" className="rounded-lg border border-gray-300 dark:border-gray-600 px-5 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
            Blog
          </Link>
        </div>
      </div>
    </div>
  );
}
