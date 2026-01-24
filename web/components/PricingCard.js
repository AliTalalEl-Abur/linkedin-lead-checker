export default function PricingCard({ title, price, period, description, features, cta, ctaOnClick, badge, featured }) {
  return (
    <div className={`bg-white border-2 rounded-xl p-8 hover:border-blue-500 transition-all duration-200 hover:shadow-lg relative ${
      featured ? 'border-blue-500 shadow-lg' : 'border-gray-200'
    }`}>
      {badge && (
        <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
          <span className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
            {badge}
          </span>
        </div>
      )}
      
      <h3 className="text-2xl font-bold text-gray-900 mb-2">{title}</h3>
      
      {price && (
        <div className="mb-4">
          <span className="text-4xl font-bold text-gray-900">${price}</span>
          {period && <span className="text-gray-600 text-lg">/{period}</span>}
        </div>
      )}
      
      <p className="text-gray-600 mb-6">{description}</p>
      
      <ul className="space-y-3 mb-8">
        {features.map((feature, index) => (
          <li key={index} className="flex items-start">
            <svg className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="text-gray-700">{feature}</span>
          </li>
        ))}
      </ul>
      
      <button 
        onClick={ctaOnClick}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-all duration-200"
      >
        {cta}
      </button>
    </div>
  );
}
