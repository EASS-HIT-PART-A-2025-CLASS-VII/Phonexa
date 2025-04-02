import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Level from "./Components/Level";
import LevelResult from "./Components/LevelResult";
import StartPage from "./Components/StartPage";
import ProtectedRoute from "./Components/ProtectedRoute";

const App = () => {
  return (
    <Router>
      <Routes>
        {/* Root Route */}
        <Route path="/" element={<StartPage />} />

        {/* Level Route */}
        <Route path="/level" element={<Level />} />

        {/* Protected LevelResult Route */}
        <Route
          path="/level-result"
          element={
            <ProtectedRoute alertMessage="You must complete the level before viewing the results.">
              <LevelResult />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
};

export default App;