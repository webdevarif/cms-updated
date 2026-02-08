import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Hello from Store Dashboard</h1>
        <p className="text-lg text-gray-600 mb-8">
          Welcome to the store administration dashboard
        </p>
        <div className="space-x-4">
          <Link
            href="/en"
            className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
          >
            English
          </Link>
          <Link
            href="/es"
            className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded"
          >
            Español
          </Link>
          <Link
            href="/fr"
            className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
          >
            Français
          </Link>
        </div>
      </div>
    </div>
  );
}
