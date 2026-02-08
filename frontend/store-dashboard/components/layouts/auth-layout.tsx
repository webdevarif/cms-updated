import React from 'react';
import Image from 'next/image';

const AuthLayout = ( {
        children
    } : {
        children: React.ReactNode
    } ) => {
  return (
    <div className='grid md:grid-cols-[7fr_5fr] md:h-screen'>
        <div className="h-full w-full md:order-2">
            {children}
        </div>
        <div className="h-full md:order-1">
            <Image className="h-full w-full object-cover object-center" src={'https://placehold.co/1600x1200'} alt="Auth Background Image" width={1600} height={1200} unoptimized/>
        </div>
    </div>
  )
}

export default AuthLayout;
