const { useState, useEffect, useRef } = React;

const App = () => {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    const handleSendMessage = async () => {
        if (inputValue.trim()) {
            const newMessage = { text: inputValue, sender: 'user', timestamp: new Date().toLocaleTimeString() };
            setMessages([...messages, newMessage]);
            setInputValue('');
            setIsLoading(true);

            try {
                const response = await fetch('/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: inputValue }),
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const data = await response.json();
                if (data.error) {
                    throw new Error(data.error);
                }

                setMessages(prevMessages => [...prevMessages, { text: data.response, sender: 'bot', timestamp: new Date().toLocaleTimeString() }]);
            } catch (error) {
                setMessages(prevMessages => [...prevMessages, { text: `Error: ${error.message}`, sender: 'bot', timestamp: new Date().toLocaleTimeString() }]);
            } finally {
                setIsLoading(false);
            }
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-header">
                ChatBit
            </div>
            <div className="chat-messages">
                {messages.map((message, index) => (
                    <ChatBubble key={index} message={message} />
                ))}
                {isLoading && <LoadingIndicator />}
                <div ref={messagesEndRef} />
            </div>
            <div className="chat-input">
                <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Type a message..."
                />
                <button onClick={handleSendMessage}>Send</button>
            </div>
        </div>
    );
};

ReactDOM.render(<App />, document.getElementById('root'));