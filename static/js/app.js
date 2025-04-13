class EcommerceApp extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            products: [],
            cart: [],
            total: 0,
            loading: true,
            error: null
        };
    }

    componentDidMount() {
        this.fetchProducts();
        this.fetchCart();
    }

    fetchProducts = async () => {
        try {
            const response = await fetch('/api/products/');
            const products = await response.json();
            this.setState({ products, loading: false });
        } catch (error) {
            this.setState({ error: 'Failed to load products', loading: false });
        }
    };

    fetchCart = async () => {
        try {
            const response = await fetch('/api/cart/');
            const cart = await response.json();
            this.setState({ cart });
            this.updateTotal();
        } catch (error) {
            console.error('Failed to load cart:', error);
        }
    };

    updateTotal = async () => {
        try {
            const response = await fetch('/api/cart/total/');
            const data = await response.json();
            this.setState({ total: data.total });
        } catch (error) {
            console.error('Failed to update total:', error);
        }
    };

    addToCart = async (productId) => {
        try {
            const response = await fetch(`/api/add-to-cart/${productId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });
            if (response.ok) {
                this.fetchCart();
            }
        } catch (error) {
            console.error('Failed to add to cart:', error);
        }
    };

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    render() {
        const { products, cart, total, loading, error } = this.state;

        if (loading) return <div>Loading...</div>;
        if (error) return <div>Error: {error}</div>;

        return (
            <div className="container">
                <h1>E-commerce Store</h1>
                
                <div className="cart-summary">
                    <h2>Cart Total: ${total}</h2>
                    <p>Items in cart: {cart.length}</p>
                </div>

                <div className="products-grid">
                    {products.map(product => (
                        <div key={product.id} className="product-card">
                            <img src={product.image} alt={product.name} />
                            <h3>{product.name}</h3>
                            <p>${product.price}</p>
                            <button onClick={() => this.addToCart(product.id)}>
                                Add to Cart
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        );
    }
}

// Render the app
const container = document.getElementById('app');
const root = ReactDOM.createRoot(container);
root.render(<EcommerceApp />); 