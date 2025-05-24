import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <p>
        {new Date().getFullYear()}. Strona do zarządzania kolekcją książek
        stworzona przez Michała Ruska, Łukasza Iwańskiego i Michała Zająca
      </p>
    </footer>
  );
};

export default Footer;