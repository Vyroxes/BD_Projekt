import './Home.css';

const Home = () => {
    return (
        <div className='home-container'>
            <h1>Aplikacja do zarządzania kolekcją książek</h1>
            <h3>
                Aplikacja służy do zarządzania wirtualną biblioteką książek, oferując szeroki zakres funkcji zarówno dla zwykłych użytkowników, jak i administratorów. Umożliwia założenie konta w sposób tradycyjny lub logowanie przy użyciu kont GitHub i Discord.
                Użytkownicy mogą dodawać książki ręcznie, przy użyciu kodu ISBN lub importując dane z pliku JSON. Każdą pozycję można przeglądać, edytować, usuwać oraz przenosić między kolekcją a listą życzeń. Dostępna jest również funkcja oceniania i recenzowania książek, co pozwala na tworzenie własnych opinii.
                Aplikacja umożliwia przeglądanie profili innych użytkowników wraz z ich statystykami. Dostępne są również płatne pakiety PREMIUM i PREMIUM+, które odblokowują dodatkowe funkcje i można je zakupić za pośrednictwem systemu Stripe.
                Panel administracyjny pozwala na zarządzanie kontami użytkowników — ich usuwanie, przeglądanie szczegółowych informacji, zmianę pakietu oraz wgląd w informacje o aplikacji, takie jak ciasteczka czy czas życia tokenów.
                W przypadku problemów dostępny jest formularz kontaktowy. Aplikacja przykłada dużą wagę do kwestii bezpieczeństwa, wdrażając odpowiednie mechanizmy ochrony danych i użytkowników.
            </h3>
        </div>
    );
};

export default Home;