export default function Section({ children, className = '', background = 'white' }) {
  const bgColors = {
    white: 'bg-white',
    gray: 'bg-gray-50',
  };

  return (
    <section className={`py-16 md:py-24 ${bgColors[background]} ${className}`}>
      <div className="container mx-auto px-4 max-w-6xl">
        {children}
      </div>
    </section>
  );
}
