import React, { useState, useEffect, useRef } from "react";

interface LogEntry {
  timestamp: string;
  ip: string;
  method: string;
  path: string;
  status: string;
  bytes: string;
  userAgent: string;
}

interface LogAnalysis {
  total_requests: number;
  status_code_distribution: Record<string, number>;
  error_count: number;
  success_rate: number;
  timestamp: string;
}

interface WebSocketMessage {
  type: "initial_data" | "update" | "error" | "summary_update";
  logs?: string;
  analysis?: LogAnalysis;
  error_logs?: string[];
  summary?: string;
  message?: string;
  timestamp?: string;
}

const Dashboard: React.FC = () => {
  const [logs, setLogs] = useState<string>("");
  const [analysis, setAnalysis] = useState<LogAnalysis | null>(null);
  const [errorLogs, setErrorLogs] = useState<string[]>([]);
  const [summary, setSummary] = useState<string>("");
  const [connectionStatus, setConnectionStatus] = useState<
    "connecting" | "connected" | "disconnected"
  >("disconnected");
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const wsRef = useRef<WebSocket | null>(null);

  const connectWebSocket = () => {
    // Prevent multiple connection attempts
    if (wsRef.current && wsRef.current.readyState === WebSocket.CONNECTING) {
      console.log("WebSocket: Already connecting, skipping new attempt.");
      return;
    }

    // Close existing connection if any
    if (wsRef.current) {
      console.log(
        "WebSocket: Closing existing connection before reconnecting."
      );
      wsRef.current.close();
    }

    setConnectionStatus("connecting");
    console.log("WebSocket: Attempting to connect...");

    // Connect to localhost:8000 since frontend runs locally and backend runs in Docker
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => {
      console.log("WebSocket connected");
      setConnectionStatus("connected");
    };

    ws.onmessage = (event) => {
      console.log("WebSocket: Message received", event.data);
      try {
        const data: WebSocketMessage = JSON.parse(event.data);

        switch (data.type) {
          case "initial_data":
            if (data.logs) setLogs(data.logs);
            if (data.analysis) setAnalysis(data.analysis);
            if (data.error_logs) setErrorLogs(data.error_logs);
            if (data.summary) setSummary(data.summary);
            setLastUpdated(new Date());
            break;

          case "update":
            if (data.analysis) setAnalysis(data.analysis);
            setLastUpdated(new Date());
            break;

          case "summary_update":
            if (data.summary) setSummary(data.summary);
            setLastUpdated(new Date());
            break;

          case "error":
            console.error("WebSocket error:", data.message);
            break;
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    ws.onclose = (event) => {
      console.log("WebSocket: Disconnected", event.code, event.reason);
      setConnectionStatus("disconnected");

      // Only attempt reconnection if the close wasn't intentional
      if (event.code !== 1000) {
        // Try to reconnect after 5 seconds
        setTimeout(() => {
          // Check if we're still disconnected before attempting reconnection
          if (connectionStatus === "disconnected") {
            console.log("WebSocket: Attempting to reconnect...");
            connectWebSocket();
          }
        }, 5000);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket: Error event", error);
      setConnectionStatus("disconnected");
    };

    wsRef.current = ws;
  };

  useEffect(() => {
    console.log("Dashboard mounted, connecting WebSocket...");
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        console.log("Dashboard unmounting, closing WebSocket...");
        wsRef.current.close(1000, "Component unmounting");
        wsRef.current = null;
      }
    };
  }, []);

  const parseLogLine = (line: string): LogEntry | null => {
    const regex =
      /^(\S+) - - \[([^\]]+)\] "(\S+) (\S+) [^"]*" (\d+) (\d+) "([^"]*)" "([^"]*)"$/;
    const match = line.match(regex);

    if (match) {
      return {
        ip: match[1],
        timestamp: match[2],
        method: match[3],
        path: match[4],
        status: match[5],
        bytes: match[6],
        userAgent: match[8],
      };
    }
    return null;
  };

  const getStatusColor = (status: string) => {
    if (status.startsWith("2")) return "text-green-600";
    if (status.startsWith("3")) return "text-blue-600";
    if (status.startsWith("4")) return "text-yellow-600";
    if (status.startsWith("5")) return "text-red-600";
    return "text-gray-600";
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case "connected":
        return "text-green-600";
      case "connecting":
        return "text-yellow-600";
      case "disconnected":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  const getConnectionStatusText = () => {
    switch (connectionStatus) {
      case "connected":
        return "Connected";
      case "connecting":
        return "Connecting...";
      case "disconnected":
        return "Disconnected";
      default:
        return "Unknown";
    }
  };

  const recentLogs = logs
    .split("\n")
    .filter((line) => line.trim())
    .slice(-10)
    .reverse();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                AutoSRE Dashboard
              </h1>
              <p className="text-gray-600">
                Real-time log monitoring and analysis
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div
                  className={`w-3 h-3 rounded-full ${getConnectionStatusColor().replace(
                    "text-",
                    "bg-"
                  )}`}
                ></div>
                <span
                  className={`text-sm font-medium ${getConnectionStatusColor()}`}
                >
                  {getConnectionStatusText()}
                </span>
              </div>
              <div className="text-sm text-gray-500">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Statistics Cards */}
        {analysis && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <svg
                    className="w-6 h-6 text-blue-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">
                    Total Requests
                  </p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {analysis.total_requests}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <svg
                    className="w-6 h-6 text-green-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">
                    Success Rate
                  </p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {analysis.success_rate.toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-2 bg-red-100 rounded-lg">
                  <svg
                    className="w-6 h-6 text-red-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Errors</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {analysis.error_count}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <svg
                    className="w-6 h-6 text-purple-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">
                    Status Codes
                  </p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {Object.keys(analysis.status_code_distribution).length}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Logs */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Recent Logs</h3>
            </div>
            <div className="overflow-hidden">
              <div className="max-h-96 overflow-y-auto">
                {recentLogs.map((log, index) => {
                  const parsedLog = parseLogLine(log);
                  return (
                    <div
                      key={index}
                      className="px-6 py-3 border-b border-gray-100 hover:bg-gray-50"
                    >
                      {parsedLog ? (
                        <div className="space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-gray-900">
                              {parsedLog.method} {parsedLog.path}
                            </span>
                            <span
                              className={`text-sm font-semibold ${getStatusColor(
                                parsedLog.status
                              )}`}
                            >
                              {parsedLog.status}
                            </span>
                          </div>
                          <div className="text-xs text-gray-500">
                            {parsedLog.timestamp} • {parsedLog.ip} •{" "}
                            {parsedLog.bytes} bytes
                          </div>
                        </div>
                      ) : (
                        <div className="text-sm text-gray-600 font-mono">
                          {log}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* AI Analysis */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">AI Analysis</h3>
            </div>
            <div className="p-6">
              {summary ? (
                <div className="prose prose-sm max-w-none">
                  <div className="whitespace-pre-wrap text-gray-700">
                    {summary}
                  </div>
                </div>
              ) : (
                <div className="text-gray-500 text-center py-8">
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                    />
                  </svg>
                  <p className="mt-2">No analysis available</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Error Logs */}
        {errorLogs.length > 0 && (
          <div className="mt-8 bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                Error Logs ({errorLogs.length})
              </h3>
            </div>
            <div className="overflow-hidden">
              <div className="max-h-64 overflow-y-auto">
                {errorLogs.map((errorLog, index) => (
                  <div
                    key={index}
                    className="px-6 py-3 border-b border-gray-100"
                  >
                    <div className="text-sm text-red-600 font-mono">
                      {errorLog}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Status Code Distribution */}
        {analysis && analysis.status_code_distribution && (
          <div className="mt-8 bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">
                Status Code Distribution
              </h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {Object.entries(analysis.status_code_distribution).map(
                  ([status, count]) => (
                    <div key={status} className="text-center">
                      <div
                        className={`text-2xl font-bold ${getStatusColor(
                          status
                        )}`}
                      >
                        {status}
                      </div>
                      <div className="text-sm text-gray-600">
                        {count} requests
                      </div>
                    </div>
                  )
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
