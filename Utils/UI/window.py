import abc
import curses

from Utils.UI.key_hints import INVENTORY_HINTS

class AbstractWindow(abc.ABC):
    """Абстрактный класс для управления окном с базовой структурой"""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height = 0
        self.width = 0
        self.hint_class = None
    
    def run(self):
        """Основной цикл окна"""
        while True:
            try:
                self.height, self.width = self.stdscr.getmaxyx()
                self.stdscr.clear()
                
                # Отображение базовой структуры окна
                self._display_header()
                self._display_body()
                self._display_footer()
                
                self.stdscr.refresh()
                
                # Обработка ввода
                key = self.stdscr.getch()
                if self._handle_input(key):
                    break
                    
            except curses.error:
                pass
            except Exception:
                pass
    
    def _display_header(self):
        """Отображение заголовка окна"""
        header_text = self.get_header_text()
        if header_text:
            self.stdscr.addstr(0, self.width // 2 - len(header_text) // 2, 
                             header_text, self.get_header_style())
            self.stdscr.addstr(1, 0, "─" * (self.width - 1), 
                             self.get_separator_style())
    
    def _display_footer(self):
        """Отображение подсказки по клавишам"""
        if self.hint_class and hasattr(self.hint_class, 'display_hints'):
            self.hint_class.display_hints(self.stdscr)

    @abc.abstractmethod
    def get_header_text(self) -> str:
        """Возвращает текст заголовка окна"""
        pass
    
    @abc.abstractmethod
    def get_key_hints(self) -> str:
        """Возвращает строку с подсказками по клавишам"""
        pass
    
    @abc.abstractmethod
    def _display_body(self):
        """Отображение основного содержимого окна"""
        pass
    
    @abc.abstractmethod
    def _handle_input(self, key: int) -> bool:
        """Обработка пользовательского ввода. Возвращает True для выхода"""
        pass
    
    def get_header_style(self):
        """Возвращает стиль заголовка"""
        return curses.A_BOLD
    
    def get_separator_style(self):
        """Возвращает стиль разделителей"""
        return curses.A_DIM
    
    def get_hints_style(self):
        """Возвращает стиль подсказок"""
        return curses.A_NORMAL


# Пример реализации конкретного класса на основе вашего инвентаря:

class InventoryWindow(AbstractWindow):
    """Конкретная реализация окна инвентаря"""
    
    def __init__(self, stdscr, players, inventory):
        super().__init__(stdscr)
        self.players = players or []
        self.inventory = inventory
        self.current_tab = 0
        self.hint_class = INVENTORY_HINTS
        
        if not self.players:
            raise ValueError("Список игроков не может быть пустым")
    
    def get_header_text(self) -> str:
        return "🎒 ИНВЕНТАРЬ"
    
    def get_key_hints(self) -> str:
        return "←→ Переключение вкладок | Q/E/ESC Выход | Enter Выбрать"
    
    def _display_body(self):
        """Отображение основного содержимого инвентаря"""
        if len(self.players) <= self.current_tab:
            return
            
        # Отображение вкладок игроков
        self._display_player_tabs()
        
        # Отображение содержимого для текущего игрока
        if self.height > 4:
            self._display_player_content()
    
    def _display_player_tabs(self):
        """Отображение вкладок с именами игроков"""
        if self.height <= 2:
            return
            
        tab_x = 2
        for i, player in enumerate(self.players):
            if i == self.current_tab:
                # Активная вкладка
                self.stdscr.addstr(2, tab_x, f" [{player.name}] ", 
                                 curses.A_BOLD)
            else:
                # Неактивная вкладка
                self.stdscr.addstr(2, tab_x, f" {player.name} ", 
                                 curses.A_NORMAL)
            tab_x += len(player.name) + 4
    
    def _display_player_content(self):
        """Отображение содержимого для текущего игрока"""
        current_player = self.players[self.current_tab]
        
        # Отображение характеристик игрока
        if self.height > 5:
            self._display_hero_stats(current_player)
        
        # Отображение инвентаря
        if self.height > 12:
            self._display_inventory_items()
    
    def _display_hero_stats(self, player):
        """Отображение характеристик героя"""
        # Здесь должна быть ваша реализация display_hero_stats_in_inventory
        pass
    
    def _display_inventory_items(self):
        """Отображение предметов инвентаря"""
        # Здесь должна быть ваша реализация отображения предметов
        pass
    
    def _handle_input(self, key: int) -> bool:
        """Обработка ввода для окна инвентаря"""
        if key in [ord('q'), ord('Q'), 27]:  # 27 = ESC
            return True
        elif key == curses.KEY_LEFT:
            self.current_tab = (self.current_tab - 1) % len(self.players)
        elif key == curses.KEY_RIGHT:
            self.current_tab = (self.current_tab + 1) % len(self.players)
        elif key == curses.KEY_RESIZE:
            return False  # Продолжить работу при ресайзе
        elif key in [10, 13]:  # Enter
            # Обработка выбора предмета
            pass
        
        return False