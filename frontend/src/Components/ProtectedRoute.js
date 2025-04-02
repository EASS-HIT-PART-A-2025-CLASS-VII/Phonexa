import { useNavigate, useLocation } from "react-router-dom";
import React from "react";

const ProtectedRoute = ({ alertMessage, children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  // Check if the user has access
  const canAccess = location.state?.canAccess;

  React.useEffect(() => {
    if (!canAccess) {
      // Display a custom message or redirect without blocking
      console.error(alertMessage || "You are not authorized to access this page.");
      navigate(-1); // Go back to the previous page
    }
  }, [canAccess, alertMessage, navigate]);

  if (!canAccess) {
    return null; // Do not render anything
  }

  return children; // Render the children if access is allowed
};

export default ProtectedRoute;