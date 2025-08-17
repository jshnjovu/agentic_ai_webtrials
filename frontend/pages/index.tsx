import { useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to templates page
    router.push('/templates');
  }, [router]);

  return (
    <>
      <Head>
        <title>Website Template Generator</title>
        <meta name="description" content="Create professional websites quickly with our template system" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Website Template Generator
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Redirecting to template gallery...
          </p>
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        </div>
      </div>
    </>
  );
}
