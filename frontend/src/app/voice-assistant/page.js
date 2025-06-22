"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import Vapi from "@vapi-ai/web";

const publicKey = "2d89a8ef-c549-475f-a2ad-0ff6e65d1689"; // Replace with your actual public key

export default function VoiceAssistant() {
  const [volumeLevel, setVolumeLevel] = useState(0);
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [conversation, setConversation] = useState([]);
  const [startingContext, setStartingContext] = useState("");
  const vapiRef = useRef(null);

  const initializeVapi = useCallback(() => {
    if (!vapiRef.current) {
      const vapiInstance = new Vapi(publicKey);
      vapiRef.current = vapiInstance;

      vapiInstance.on("call-start", async () => {
        setIsSessionActive(true);

        // Send starting context if provided
        if (startingContext.trim()) {
          vapiInstance.send({
            type: "add-message",
            message: {
              role: "system",
              content: startingContext,
            },
          });

          setConversation((prev) => [
            ...prev,
            { role: "system", text: startingContext },
          ]);
        }
      });

      vapiInstance.on("call-end", () => {
        setIsSessionActive(false);
        setConversation([]); // Reset conversation on call end
      });

      vapiInstance.on("volume-level", (volume) => {
        setVolumeLevel(volume);
      });

      vapiInstance.on("message", (message) => {
        if (
          message.type === "transcript" &&
          message.transcriptType === "final"
        ) {
          setConversation((prev) => [
            ...prev,
            { role: message.role, text: message.transcript },
          ]);
        }
      });

      vapiInstance.on("error", (e) => {
        console.error("Vapi error:", e);
      });
    }
  }, [startingContext]);

  useEffect(() => {
    initializeVapi();

    // Cleanup function to end call and dispose Vapi instance
    return () => {
      if (vapiRef.current) {
        vapiRef.current.stop();
        vapiRef.current = null;
      }
    };
  }, [initializeVapi]);

  const toggleCall = async () => {
    try {
      if (isSessionActive) {
        await vapiRef.current.stop();
      } else {
        await vapiRef.current.start({
            model: {
              provider: "openai",
              model: "gpt-3.5-turbo",
              messages: [
                {
                  role: "system",
                  content: "You are an assistant.",
                },
               ],
             },
             voice: {
              provider: "11labs",
              voiceId: "burt",
            },
            
          });
      }
    } catch (err) {
      console.error("Error toggling Vapi session:", err);
    }
  };

  const handleContextChange = (e) => {
    setStartingContext(e.target.value);
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-800">
          Voice Assistant Test
        </h1>

        {/* Starting Context Input */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">
            Starting Context
          </h2>
          <textarea
            value={startingContext}
            onChange={handleContextChange}
            placeholder="Enter starting context for the assistant (e.g., 'You are a helpful customer service agent for a bookstore.')"
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows="3"
            disabled={isSessionActive}
          />
          <p className="text-sm text-gray-500 mt-2">
            This context will be sent to the assistant when the call starts.
          </p>
        </div>

        {/* Voice Assistant Controls */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex flex-col items-center space-y-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={toggleCall}
                className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
                  isSessionActive
                    ? "bg-red-500 hover:bg-red-600 text-white"
                    : "bg-green-500 hover:bg-green-600 text-white"
                }`}
              >
                {isSessionActive ? "🛑 End Call" : "🎤 Start Call"}
              </button>

              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Status:</span>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${
                    isSessionActive
                      ? "bg-green-100 text-green-800"
                      : "bg-gray-100 text-gray-800"
                  }`}
                >
                  {isSessionActive ? "Active" : "Inactive"}
                </span>
              </div>
            </div>

            {/* Volume Level Indicator */}
            {isSessionActive && (
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">Volume:</span>
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-100"
                    style={{ width: `${Math.min(volumeLevel * 100, 100)}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Conversation Display */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">
            Conversation Log
          </h2>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {conversation.length === 0 ? (
              <p className="text-gray-500 italic">No conversation yet...</p>
            ) : (
              conversation.map((message, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg ${
                    message.role === "user"
                      ? "bg-blue-100 text-blue-800 ml-4"
                      : message.role === "assistant"
                      ? "bg-green-100 text-green-800 mr-4"
                      : "bg-gray-100 text-gray-700"
                  }`}
                >
                  <div className="text-xs font-medium mb-1 uppercase">
                    {message.role}
                  </div>
                  <div className="text-sm">{message.text}</div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
          <h3 className="font-semibold text-blue-800 mb-2">How to use:</h3>
          <ol className="text-blue-700 text-sm space-y-1">
            <li>
              1. (Optional) Add starting context to guide the assistant's
              behavior
            </li>
            <li>2. Click "Start Call" to begin the voice session</li>
            <li>3. Speak naturally - the assistant will respond via voice</li>
            <li>4. Watch the conversation log to see the transcript</li>
            <li>5. Click "End Call" when finished</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
