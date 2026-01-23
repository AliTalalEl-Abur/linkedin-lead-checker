export default function Button({ children, variant = 'primary', onClick, className = '' }) {
  const baseStyles = 'font-semibold px-8 py-4 rounded-lg transition-all duration-200 inline-block text-center';
  
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white shadow-md hover:shadow-lg',
    secondary: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50',
  };

  return (
    <button
      onClick={onClick}
      className={`${baseStyles} ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
}
