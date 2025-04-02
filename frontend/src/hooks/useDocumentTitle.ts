import { useEffect } from 'react';

/**
 * A custom hook to set the document title
 * @param title - The title to set for the current page
 */
const useDocumentTitle = (title: string): void => {
  useEffect(() => {
    // Save the original title
    const originalTitle = document.title;
    
    // Set the new title
    document.title = title;
    
    // Restore the original title when the component unmounts
    return () => {
      document.title = originalTitle;
    };
  }, [title]);
};

export default useDocumentTitle;