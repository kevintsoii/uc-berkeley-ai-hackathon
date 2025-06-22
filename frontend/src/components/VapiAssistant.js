"use client";
import React, { useState, useEffect } from 'react';
import Vapi from '@vapi-ai/web';
import VapiClient from '@vapi-ai/server-sdk';

// const client = new VapiClient({
//     token: process.env.VAPI_API_KEY
// });

const VapiAssistant = ({ 
  apiKey, 
  assistantId, 
  language = "en", 
  formType = "I-130",
  heading = "General Information",
  backendUrl = "http://localhost:8000",
  config = {}
}) => {
  const [vapi, setVapi] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState([]);
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateError, setUpdateError] = useState(null);
  const [updateSuccess, setUpdateSuccess] = useState(false);

  useEffect(() => {
    
    const vapiInstance = new Vapi(apiKey);
    setVapi(vapiInstance);

    // Event listeners
    vapiInstance.on('call-start', () => {
      console.log('Call started');
      setIsConnected(true);
    });

    vapiInstance.on('call-end', () => {
      console.log('Call ended');
      setIsConnected(false);
      setIsSpeaking(false);
    });

    vapiInstance.on('speech-start', () => {
      console.log('Assistant started speaking');
      setIsSpeaking(true);
    });

    vapiInstance.on('speech-end', () => {
      console.log('Assistant stopped speaking');
      setIsSpeaking(false);
    });

    vapiInstance.on('message', (message) => {
      if (message.type === 'transcript') {
        setTranscript(prev => [...prev, {
          role: message.role,
          text: message.transcript
        }]);
      }
    });

    vapiInstance.on('error', (error) => {
      console.error('Vapi error:', error);
    });

    return () => {
      vapiInstance?.stop();
    };
  }, [apiKey]);

  // Function to update the assistant with context and language
  const updateAssistant = async () => {
    setIsUpdating(true);
    setUpdateError(null);
    setUpdateSuccess(false);
    
    try {
      console.log('Updating assistant with:', {
        language,
        heading,
        formType,
        assistantId,
        backendUrl
      });

      const response = await fetch(`${backendUrl}/assistant/${assistantId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          language: language,
          heading: heading,
          form_type: formType
        })
      });

      console.log('Backend response status:', response.status);
      console.log('Backend response headers:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Backend error response:', errorText);
        throw new Error(`Failed to update assistant: ${response.status} ${response.statusText} - ${errorText}`);
      }

      const result = await response.json();
      console.log('Assistant updated successfully:', result);
      setUpdateSuccess(true);
      return true;
    } catch (error) {
      console.error('Error updating assistant:', error);
      setUpdateError(error.message);
      return false;
    } finally {
      setIsUpdating(false);
    }
  };

  const startCall = async () => {
    if (vapi) {
      // First update the assistant with context and language
      const updateSuccess = await updateAssistant();
      
      if (updateSuccess) {
        // Then start the call
        console.log('Starting call with updated assistant');
        vapi.start(assistantId);
      } else {
        // If update fails, still try to start the call with existing configuration
        console.warn('Failed to update assistant, starting call with existing configuration');
        setUpdateError('Assistant update failed, but starting call with existing settings');
        vapi.start(assistantId);
      }
    }
  };

  const endCall = () => {
    if (vapi) {
      vapi.stop();
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 font-sans">
      {!isConnected ? (
        <div className="flex flex-col items-end space-y-2">
          {updateError && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded-lg text-sm max-w-xs">
              <strong>Update Error:</strong> {updateError}
            </div>
          )}
          {updateSuccess && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-2 rounded-lg text-sm max-w-xs">
              <strong>✅ Success!</strong> Assistant updated with {language} language for {heading}
            </div>
          )}
          <button
            onClick={startCall}
            disabled={isUpdating}
            className={`bg-blue-500 hover:bg-blue-600 text-white rounded-full px-8 py-4 font-bold cursor-pointer shadow-lg hover:shadow-xl transition-all duration-300 ease-in-out hover:-translate-y-0.5 ${
              isUpdating ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {isUpdating ? '🔄 Updating...' : '🎤 Talk to Assistant'}
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-xl p-5 w-80 shadow-2xl border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${
                isSpeaking 
                  ? 'bg-red-500 animate-pulse' 
                  : 'bg-teal-500'
              }`}></div>
              <span className="font-bold text-gray-800">
                {isSpeaking ? 'Assistant Speaking...' : 'Listening...'}
              </span>
            </div>
            <button
              onClick={endCall}
              className="bg-red-500 hover:bg-red-600 text-white border-none rounded-md px-3 py-1.5 text-xs cursor-pointer transition-colors"
            >
              End Call
            </button>
          </div>
          
          <div className="max-h-48 overflow-y-auto mb-3 p-2 bg-gray-50 rounded-lg">
            {transcript.length === 0 ? (
              <p className="text-gray-600 text-sm m-0">
                Conversation will appear here...
              </p>
            ) : (
              transcript.map((msg, i) => (
                <div
                  key={i}
                  className={`mb-2 ${
                    msg.role === 'user' ? 'text-right' : 'text-left'
                  }`}
                >
                  <span className={`inline-block px-3 py-2 rounded-xl text-sm max-w-[80%] text-white ${
                    msg.role === 'user' 
                      ? 'bg-teal-500' 
                      : 'bg-gray-800'
                  }`}>
                    {msg.text}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default VapiAssistant;

// Usage in your app:
// <VapiAssistant 
//   apiKey="your_public_api_key" 
//   assistantId="your_assistant_id" 
//   language="es"                    // Language code (en, es, zh, hi, ar, pt, ru, fr, de, ja)
//   formType="I-130"                 // Form type being filled (I-130, I-140, I-485, etc.)
//   heading="Personal Information"   // Current section/field being worked on
//   backendUrl="http://localhost:8000" // Backend API URL for updating assistant
// />
//
// Features:
// - Updates assistant with context and language before starting call
// - Shows loading state while updating assistant
// - Falls back to existing configuration if update fails
// - Supports multiple languages for voice interaction
// - Provides real-time conversation transcript
