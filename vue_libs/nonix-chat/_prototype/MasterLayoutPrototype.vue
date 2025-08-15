<script setup> 
import { ref } from 'vue';
import Avatar from 'primevue/avatar';

// --- Reactive State ---
const activeFavorite = ref('Account');

// --- Navigation Data ---
const mainNavItems = ref([
  { icon: 'pi pi-home', label: 'Home' },
  { icon: 'pi pi-bookmark', label: 'Bookmark' },
  { icon: 'pi pi-users', label: 'People' },
  { icon: 'pi pi-comment', label: 'Messages' },
  { icon: 'pi pi-calendar', label: 'Calendar' },
]);

const favoritesNavItems = ref([
  { icon: 'pi pi-user', label: 'Account' },
  { icon: 'pi pi-lock', label: 'Permissions' },
  { icon: 'pi pi-users', label: 'Saved Profiles' },
  { icon: 'pi pi-eye', label: 'Privacy' },
]);

// --- Event Handlers ---
const setActiveFavorite = (itemLabel) => {
  activeFavorite.value = itemLabel;
};

// --- Inline Component Definitions ---

const Sidebar = {
  setup() {
    return {
      mainNavItems,
      favoritesNavItems,
      activeFavorite,
      setActiveFavorite,
    };
  },
  components: {
    Avatar
  },
  template: `
    <div class="sidebar-container">
      <div class="sidebar-icons">
        <div class="logo-icon-wrapper">
            <svg width="32" height="32" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg" class="logo-icon">
                <path d="M18 3C9.71573 3 3 9.71573 3 18C3 26.2843 9.71573 33 18 33C26.2843 33 33 26.2843 33 18C33 9.71573 26.2843 3 18 3Z" fill="white" fill-opacity="0.1"/>
                <path d="M10.057 23.943C12.013 25.983 14.861 27.25 18 27.25C21.139 27.25 23.987 25.983 25.943 23.943C25.961 23.925 25.978 23.907 25.995 23.889C24.444 22.74 22.56 22 20.5 22C18.44 22 16.556 22.74 15.005 23.889C15.022 23.907 15.039 23.925 15.057 23.943" fill="white"/>
                <path d="M10.005 15.111C11.556 13.96 13.44 13.25 15.5 13.25C17.56 13.25 19.444 13.96 20.995 15.111C20.978 15.093 20.961 15.075 20.943 15.057C18.987 13.017 16.139 11.75 13 11.75C9.861 11.75 7.013 13.017 5.057 15.057C5.039 15.075 5.022 15.093 5.005 15.111" fill="white"/>
            </svg>
        </div>
        <nav class="main-nav">
          <a href="#" v-for="item in mainNavItems" :key="item.label" class="nav-icon-item" :aria-label="item.label">
            <i :class="item.icon"></i>
          </a>
        </nav>
        <div class="sidebar-bottom-icon">
          <Avatar image="https://placehold.co/40x40/E0E0E0/333333?text=A" size="large" shape="circle" />
        </div>
      </div>
      <div class="sidebar-menu">
        <div class="sidebar-header">
          <h2>Favorites</h2>
        </div>
        <nav class="favorites-nav">
          <ul>
            <li v-for="item in favoritesNavItems" :key="item.label">
              <a href="#" @click.prevent="setActiveFavorite(item.label)" :class="{ 'active': activeFavorite === item.label }">
                <i :class="item.icon"></i>
                <span>{{ item.label }}</span>
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  `
};

const Header = {
  components: {
    Avatar
  },
  template: `
    <header class="app-header">
      <div class="header-actions">
        <button class="header-icon-btn" aria-label="Inbox">
          <i class="pi pi-inbox"></i>
        </button>
        <button class="header-icon-btn" aria-label="Favorites">
          <i class="pi pi-star"></i>
        </button>
        <button class="header-icon-btn" aria-label="Contacts">
          <i class="pi pi-id-card"></i>
        </button>
      </div>
      <div class="header-profile">
        <Avatar image="https://placehold.co/32x32/E0E0E0/777777?text=U" size="normal" shape="circle" />
      </div>
    </header>
  `
};

const MainContent = {
  template: `<main class="main-content"></main>`
};

</script>

<template>
  <div id="app-layout">
    <Sidebar />
    <div class="main-panel">
      <Header />
      <MainContent />
    </div>
  </div>
</template>

<style>
/* Global Styles & PrimeVue Overrides */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import 'primeicons/primeicons.css';

:root {
  --sidebar-icon-bg: #047857;
  --sidebar-menu-bg: #10B981;
  --sidebar-active-bg: #059669;
  --text-color-light: #FFFFFF;
  --text-color-light-secondary: #A7F3D0;
  --text-color-dark: #374151;
  --border-color: #E5E7EB;
  --background-color: #FFFFFF;
}

body {
  margin: 0;
  font-family: 'Inter', sans-serif;
  background-color: var(--background-color);
  color: var(--text-color-dark);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app-layout {
  display: flex;
  height: 100vh;
}

/* Sidebar Component Styles */
.sidebar-container {
  display: flex;
  width: 280px;
  flex-shrink: 0;
}

.sidebar-icons {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 64px;
  background-color: var(--sidebar-icon-bg);
  padding: 1rem 0;
  color: var(--text-color-light);
}

.logo-icon-wrapper {
    padding-bottom: 2rem;
    padding-top: 0.25rem;
}

.logo-icon {
    width: 32px;
    height: 32px;
}

.main-nav {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
  align-items: center;
}

.nav-icon-item {
  color: var(--text-color-light-secondary);
  font-size: 1.25rem;
  transition: color 0.2s;
}

.nav-icon-item:hover {
  color: var(--text-color-light);
}

.sidebar-bottom-icon {
  margin-top: auto;
}

.sidebar-bottom-icon .p-avatar {
    width: 36px;
    height: 36px;
}

.sidebar-menu {
  flex-grow: 1;
  background-color: var(--sidebar-menu-bg);
  color: var(--text-color-light);
  padding: 1.5rem 1rem;
}

.sidebar-header h2 {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 1.5rem 0.5rem;
  color: var(--text-color-light);
}

.favorites-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.favorites-nav li a {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  text-decoration: none;
  color: var(--text-color-light);
  font-weight: 500;
  transition: background-color 0.2s;
}

.favorites-nav li a:hover {
  background-color: var(--sidebar-active-bg);
}

.favorites-nav li a.active {
  background-color: var(--sidebar-active-bg);
}

.favorites-nav li a i {
  margin-right: 0.75rem;
  font-size: 1rem;
  width: 20px;
  text-align: center;
}

/* Main Panel Styles */
.main-panel {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  background-color: #FFFFFF;
}

/* Header Component Styles */
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border-color);
  background-color: #FFFFFF;
  height: 65px;
  box-sizing: border-box;
  flex-shrink: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #6B7280;
  font-size: 1.25rem;
  padding: 0.5rem;
}

.header-icon-btn:hover {
  color: #111827;
}

.header-profile .p-avatar {
  width: 32px;
  height: 32px;
}

/* Main Content Styles */
.main-content {
  flex-grow: 1;
  padding: 1.5rem;
  background-color: #F9FAFB;
}
</style>