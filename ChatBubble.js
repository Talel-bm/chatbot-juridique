const ChatBubble = ({ message }) => {
    return (
        <div className={`message ${message.sender}`}>
            <div className="message-text">
                {message.text}
            </div>
        </div>
    );
};

export default ChatBubble;