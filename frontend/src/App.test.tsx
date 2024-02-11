import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders home page', () => {
  render(<App />);
  expect(screen.getByText(/Word Wolf/i)).toBeInTheDocument();
});
