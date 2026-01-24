"""
Modern UI Design System with Gradients, Glassmorphism, and Animations
"""

# Modern Vibrant Color Palette with HSL-based harmonious colors
THEME_COLORS = {
    # Primary Gradient Colors (Purple to Blue)
    "gradient_start": "#8B5CF6",     # Vibrant Purple
    "gradient_mid": "#6366F1",       # Indigo
    "gradient_end": "#3B82F6",       # Bright Blue
    "gradient_accent": "#EC4899",    # Pink accent
    
    # Functional Colors
    "success": "#10B981",            # Modern Green
    "success_hover": "#059669",
    "danger": "#EF4444",             # Modern Red
    "danger_hover": "#DC2626",
    "warning": "#F59E0B",            # Amber
    "info": "#06B6D4",               # Cyan
    
    # Neutral Colors (Dark Theme)
    "background": "#0F172A",         # Dark Slate
    "background_light": "#1E293B",   # Lighter Slate
    "surface": "#334155",            # Card Surface
    "surface_light": "#475569",      # Lighter Surface
    
    # Text Colors
    "text": "#F8FAFC",               # Almost White
    "text_secondary": "#CBD5E1",     # Light Gray
    "text_muted": "#94A3B8",         # Muted Gray
    
    # Glassmorphism (using solid colors since CustomTkinter doesn't support RGBA)
    "glass_bg": "#1E293B",                # Semi-transparent dark equivalent
    "glass_border": "#475569",            # Subtle border
    "glass_highlight": "#334155",         # Top highlight
}

# Animation timing functions
ANIMATIONS = {
    "fast": 150,      # milliseconds
    "normal": 250,
    "slow": 400,
    "ease": "cubic-bezier(0.4, 0, 0.2, 1)",
}

# Shadows for depth
SHADOWS = {
    "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
    "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
    "glow": "0 0 20px rgba(139, 92, 246, 0.4)",
}

# Spacing scale
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
    "2xl": 48,
}

# Border radius scale
RADIUS = {
    "sm": 6,
    "md": 10,
    "lg": 16,
    "xl": 24,
    "full": 9999,
}

# Typography
FONTS = {
    "primary": "Segoe UI",
    "secondary": "Inter",
    "mono": "Consolas",
}

# Helper functions for CustomTkinter
def get_gradient_colors():
    """Returns tuple of gradient colors for background"""
    return (THEME_COLORS["gradient_start"], THEME_COLORS["gradient_end"])

def get_button_colors(type="primary"):
    """Get button colors based on type"""
    colors = {
        "primary": (THEME_COLORS["gradient_mid"], THEME_COLORS["gradient_start"]),
        "success": (THEME_COLORS["success"], THEME_COLORS["success_hover"]),
        "danger": (THEME_COLORS["danger"], THEME_COLORS["danger_hover"]),
        "warning": (THEME_COLORS["warning"], "#D97706"),
        "secondary": (THEME_COLORS["surface"], THEME_COLORS["surface_light"]),
    }
    return colors.get(type, colors["primary"])

def get_glass_style():
    """Returns dict for glassmorphic styling"""
    return {
        "fg_color": THEME_COLORS["glass_bg"],
        "border_width": 1,
        "border_color": THEME_COLORS["glass_border"],
        "corner_radius": RADIUS["lg"],
    }

# CustomTkinter specific configurations
CTK_THEME = {
    "appearance_mode": "dark",
    "default_color_theme": "blue",
    
    "CTkFrame": {
        "fg_color": THEME_COLORS["background_light"],
        "corner_radius": RADIUS["md"],
    },
    
    "CTkButton": {
        "fg_color": THEME_COLORS["gradient_mid"],
        "hover_color": THEME_COLORS["gradient_start"],
        "corner_radius": RADIUS["md"],
        "border_width": 0,
        "font": (FONTS["primary"], 14, "bold"),
        "height": 45,
    },
    
    "CTkEntry": {
        "fg_color": THEME_COLORS["surface"],
        "border_color": THEME_COLORS["surface_light"],
        "corner_radius": RADIUS["md"],
        "border_width": 2,
        "height": 50,
        "font": (FONTS["primary"], 16),
    },
    
    "CTkLabel": {
        "text_color": THEME_COLORS["text"],
        "font": (FONTS["primary"], 14),
    },
}

# Additional UI helper functions
def create_card_frame(parent, **kwargs):
    """Create a modern card-style frame with shadow effect"""
    import customtkinter as ctk
    
    defaults = {
        "fg_color": THEME_COLORS["background_light"],
        "corner_radius": RADIUS["lg"],
        "border_width": 1,
        "border_color": THEME_COLORS["surface"],
    }
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)

def create_glass_frame(parent, **kwargs):
    """Create a glassmorphic frame"""
    import customtkinter as ctk
    
    defaults = get_glass_style()
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)

def create_gradient_label(parent, text, **kwargs):
    """Create a label with gradient-style text color"""
    import customtkinter as ctk
    
    defaults = {
        "text": text,
        "text_color": THEME_COLORS["gradient_accent"],
        "font": (FONTS["primary"], 24, "bold"),
    }
    defaults.update(kwargs)
    return ctk.CTkLabel(parent, **defaults)

def get_status_color(status):
    """Get color based on status (e.g., stock levels)"""
    status_map = {
        "high": THEME_COLORS["success"],
        "medium": THEME_COLORS["warning"],
        "low": THEME_COLORS["danger"],
        "out": THEME_COLORS["text_muted"],
    }
    return status_map.get(status, THEME_COLORS["text"])

# Icon replacements (using Unicode symbols)
ICONS = {
    "user": "👤",
    "logout": "🚪",
    "cart": "🛒",
    "search": "🔍",
    "add": "➕",
    "delete": "🗑️",
    "edit": "✏️",
    "check": "✓",
    "close": "✕",
    "product": "📦",
    "money": "💰",
    "settings": "⚙️",
    "report": "📊",
    "box": "📦",
    "star": "⭐",
}
