import { useState, useEffect, useRef, useCallback } from "react";
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from "react-router-dom";
import { PayPalScriptProvider, PayPalButtons } from "@paypal/react-paypal-js";
import { create } from "zustand";
import "@/App.css";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { Button } from "@/components/ui/button";
import PersistentMediaPlayer from "@/components/PersistentMediaPlayer";
import { useMediaPlayer } from "@/hooks/useMediaPlayer";
import AICanvas from "@/components/AICanvas";
import AICanvasEnhanced from "@/components/AICanvasEnhanced";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  MessageSquare, Image, Video, Mic, MicOff, Send, Plus, Trash2, Volume2,
  Loader2, Sparkles, Zap, Menu, X, Download, User, LogOut, Crown, Music,
  FileCode, FolderOpen, Hammer, Eye, Code, Settings, CreditCard, Edit, Save,
  Terminal, Play, ChevronRight, File, Folder, RefreshCw, Copy, Check,
  Maximize2, Minimize2, Heart, Share2, ShoppingCart, TrendingUp,
  Wand2, FileImage, Film, ListMusic, Search, Play as PlayIcon, SkipBack, SkipForward,
  Volume, Clock, Disc3, Grid, List as ListIcon, Shuffle, Repeat,
  Podcast, BookOpen, Tv, Gamepad2, Gem, Calendar, Link as LinkIcon, Mail,
  Gift as DonateIcon, Globe, QrCode, Users, ListVideo, Brain, Zap as Analytics, HardDrive
} from "lucide-react";
import Editor from "@monaco-editor/react";
import PWAInstallBanner from "@/components/PWAInstallBanner";

// Enterprise Services Tab Components
import PodcastTab from "@/components/PodcastTab";
import AdaptiveELearningTab from "@/components/AdaptiveELearningTab";
import VideoEditorTab from "@/components/VideoEditorTab";
import GamingTab from "@/components/GamingTab";
import NFTTab from "@/components/NFTTab";
import LiveShoppingTab from "@/components/LiveShoppingTab";

// AI Tutoring Platform
import AITutoringPlatform from "@/pages/AITutoringPlatform";
import AdaptiveELearningPage from "@/pages/AdaptiveELearningPage";
import PeerLearningPage from "@/pages/PeerLearningPage";
import ContentGenerationPage from "@/pages/ContentGenerationPage";
import ECommerceTab from "@/components/ECommerceTab";
import SubscriptionTab from "@/components/SubscriptionTab";
import EventsTab from "@/components/EventsTab";
import AffiliateTab from "@/components/AffiliateTab";
import NewsletterTab from "@/components/NewsletterTab";
import DonationTab from "@/components/DonationTab";
import TranslationTab from "@/components/TranslationTab";
import QRCodeTab from "@/components/QRCodeTab";
import DuetTab from "@/components/DuetTab";
import { DuetCollabVideoEditor } from "@/components/DuetCollabVideoEditor";
import PlaylistTab from "@/components/PlaylistTab";
import RecommendationTab from "@/components/RecommendationTab";
import BackupTab from "@/components/BackupTab";
import ServicesMenu from "@/components/ServicesMenu";
import ImageEditorAdvanced from "@/components/ImageEditorAdvanced";

// Modern Dashboards
import ModernCreatorDashboard from "@/components/ModernCreatorDashboard";
import ModernECommerceDashboard from "@/components/ModernECommerceDashboard";
import ModernDuetCollabDashboard from "@/components/ModernDuetCollabDashboard";
import NewsletterDashboard from "@/components/NewsletterDashboard";
import QRCodeDashboard from "@/components/QRCodeDashboard";
import FilterStudio from "@/components/FilterStudio";
import AIFilterStudio from "@/components/AIFilterStudio";
import { FileExplorer, CodeExecutionPanel, TerminalPanel, PackageManagerPanel } from "@/components/BuildPageEnhancements";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Zustand store for auth
const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem("gaaius_token"),
  setUser: (user) => set({ user }),
  setToken: (token) => {
    if (token) localStorage.setItem("gaaius_token", token);
    else localStorage.removeItem("gaaius_token");
    set({ token });
  },
  logout: () => {
    localStorage.removeItem("gaaius_token");
    set({ user: null, token: null });
  }
}));

// API helper with auth
const api = axios.create({ baseURL: API });
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("gaaius_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Mode configurations - Keep original only
const MODES = {
  chat: { icon: MessageSquare, label: "Chat", color: "text-purple-400", bgColor: "bg-purple-500/20", borderColor: "border-purple-500/30", group: 1 },
  image: { icon: Image, label: "Image", color: "text-cyan-400", bgColor: "bg-cyan-500/20", borderColor: "border-cyan-500/30", group: 1 },
  video: { icon: Video, label: "Video", color: "text-orange-400", bgColor: "bg-orange-500/20", borderColor: "border-orange-500/30", group: 2 },
  audio: { icon: Music, label: "Audio", color: "text-green-400", bgColor: "bg-green-500/20", borderColor: "border-green-500/30", group: 2 },
  file: { icon: FileCode, label: "Files", color: "text-pink-400", bgColor: "bg-pink-500/20", borderColor: "border-pink-500/30", group: 2 },
  socials: { icon: Heart, label: "Socials", color: "text-pink-500", bgColor: "bg-pink-500/20", borderColor: "border-pink-500/30", group: 3 },
  imageResizer: { icon: Wand2, label: "Image Resizer", color: "text-blue-400", bgColor: "bg-blue-500/20", borderColor: "border-blue-500/30", group: 3 },
  imageConverter: { icon: FileImage, label: "Image Converter", color: "text-indigo-400", bgColor: "bg-indigo-500/20", borderColor: "border-indigo-500/30", group: 3 },
  multiTube: { icon: Film, label: "MultiTube", color: "text-red-400", bgColor: "bg-red-500/20", borderColor: "border-red-500/30", group: 4 },
  music: { icon: ListMusic, label: "Music", color: "text-green-500", bgColor: "bg-green-500/20", borderColor: "border-green-500/30", group: 4 },
  aiFilterStudio: { icon: Sparkles, label: "AI Filters", color: "text-cyan-400", bgColor: "bg-cyan-500/20", borderColor: "border-cyan-500/30", group: 4 }
};

// Marketplace and Ads configurations (hidden from modes tab, shown in menu bar separately)
const EXTERNAL_SERVICES = {
  marketplace: { icon: ShoppingCart, label: "Marketplace", color: "text-emerald-400" },
  ads: { icon: TrendingUp, label: "Ads", color: "text-amber-400" }
};

// 19 Enterprise Services - Organized Menu (NOT in MODES, only in menu sidebar)
const ENTERPRISE_SERVICES_MENU = {
  "Content & Streaming": [
    { id: "podcast", icon: Podcast, label: "Podcast", color: "text-purple-600" },
    { id: "elearning", icon: BookOpen, label: "E-Learning", color: "text-blue-600" },
    { id: "aiTutoring", icon: Brain, label: "AI Tutoring", color: "text-emerald-600" },
    { id: "videoEditor", icon: Tv, label: "Video Editor", color: "text-red-600" },
    { id: "streamingAnalytics", icon: Analytics, label: "Streaming Analytics", color: "text-sky-600" }
  ],
  "Creator Tools": [
    { id: "aiCanvas", icon: Wand2, label: "AI Canvas", color: "text-indigo-600" },
    { id: "gaming", icon: Gamepad2, label: "Gaming", color: "text-yellow-600" },
    { id: "nft", icon: Gem, label: "NFT Marketplace", color: "text-pink-600" },
    { id: "duets", icon: Users, label: "Duets", color: "text-orange-600" },
    { id: "playlists", icon: ListMusic, label: "Playlists", color: "text-violet-600" }
  ],
  "Commerce": [
    { id: "liveShopping", icon: ShoppingCart, label: "Live Shopping", color: "text-green-600" },
    { id: "ecommerce", icon: ShoppingCart, label: "E-Commerce", color: "text-lime-600" },
    { id: "subscriptions", icon: CreditCard, label: "Subscriptions", color: "text-amber-600" },
    { id: "affiliate", icon: LinkIcon, label: "Affiliate", color: "text-emerald-600" }
  ],
  "Monetization": [
    { id: "newsletter", icon: Mail, label: "Newsletter", color: "text-cyan-600" },
    { id: "donations", icon: DonateIcon, label: "Donations", color: "text-rose-600" },
    { id: "recommendations", icon: Brain, label: "Recommendations", color: "text-fuchsia-600" }
  ],
  "Utilities": [
    { id: "translation", icon: Globe, label: "Translation", color: "text-teal-600" },
    { id: "qrcode", icon: QrCode, label: "QR Code", color: "text-slate-600" },
    { id: "events", icon: Calendar, label: "Events", color: "text-indigo-600" },
    { id: "backup", icon: HardDrive, label: "Backup", color: "text-gray-600" }
  ]
};

// Enterprise folder structure for AI Builder projects
const ENTERPRISE_PROJECT_STRUCTURE = {
  frontend: {
    "public/": {
      "index.html": "<!-- Entry point -->",
      "favicon.ico": "",
      "manifest.json": '{"name": "App", "short_name": "App"}'
    },
    "src/": {
      "app/": {
        "layout.tsx": "// App layout",
        "page.tsx": "// Main page"
      },
      "components/": {
        "ui/": {},
        "layout/": {}
      },
      "features/": {
        "auth/": {},
        "feed/": {},
        "profile/": {}
      },
      "store/": {},
      "hooks/": {},
      "services/": {},
      "styles/": {},
      "utils/": {}
    },
    "package.json": "",
    "tailwind.config.js": "",
    "vite.config.ts": ""
  },
  backend: {
    "api-gateway/": {
      "src/": {
        "routes/": {},
        "middlewares/": {},
        "auth/": {}
      }
    },
    "services/": {
      "auth-service/": {},
      "user-service/": {},
      "media-service/": {}
    },
    "schemas/": {},
    "database/": {
      "migrations/": {},
      "seed/": {}
    }
  },
  mobile: {
    "pwa/": {},
    "android/": {},
    "ios/": {}
  },
  shared: {
    "types/": {},
    "constants/": {},
    "validation/": {},
    "sdk/": {}
  },
  config: {
    "app.json": "",
    "build.json": "",
    "features.json": "",
    "ai-rules.json": ""
  },
  "ai-engine": {
    "planners/": {},
    "generators/": {},
    "validators/": {},
    "prompts/": {}
  }
};

// Auth Modal Component
const AuthModal = ({ open, onClose, onSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [emailError, setEmailError] = useState("");
  const { setUser, setToken } = useAuthStore();

  // Validate Gmail only
  const validateEmail = (email) => {
    const gmailRegex = /^[a-zA-Z0-9._%+-]+@gmail\.com$/i;
    if (!email) return "Email is required";
    if (!gmailRegex.test(email)) return "Only Gmail addresses are allowed";
    return "";
  };

  const handleEmailChange = (e) => {
    const newEmail = e.target.value;
    setEmail(newEmail);
    setEmailError(validateEmail(newEmail));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate Gmail
    const error = validateEmail(email);
    if (error) {
      setEmailError(error);
      toast.error(error);
      return;
    }
    
    setLoading(true);
    try {
      const endpoint = isLogin ? "/auth/login" : "/auth/register";
      const data = isLogin ? { email, password } : { email, password, name };
      const res = await api.post(endpoint, data);
      setToken(res.data.token);
      setUser(res.data.user);
      toast.success(isLogin ? "Welcome back!" : "Account created!");
      onSuccess?.();
      onClose();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="glass border-white/10 max-w-md">
        <DialogHeader>
          <DialogTitle className="font-secondary">{isLogin ? "Welcome Back" : "Create Account"}</DialogTitle>
          <DialogDescription>Sign in with your Gmail account</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <Input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} className="bg-white/5 border-white/10" required />
          )}
          <div>
            <Input 
              type="email" 
              placeholder="your.email@gmail.com" 
              value={email} 
              onChange={handleEmailChange} 
              className={`bg-white/5 border-white/10 ${emailError ? 'border-red-500' : ''}`} 
              required 
            />
            {emailError && <p className="text-red-400 text-xs mt-1">{emailError}</p>}
          </div>
          <Input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className="bg-white/5 border-white/10" required minLength={6} />
          <Button type="submit" className="w-full bg-primary hover:bg-primary/90" disabled={loading || !!emailError}>
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : (isLogin ? "Sign In" : "Sign Up")}
          </Button>
          <p className="text-center text-sm text-muted-foreground">
            {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
            <button type="button" onClick={() => setIsLogin(!isLogin)} className="text-primary hover:underline">
              {isLogin ? "Sign up" : "Sign in"}
            </button>
          </p>
        </form>
      </DialogContent>
    </Dialog>
  );
};

// Profile Modal Component
const ProfileModal = ({ open, onClose }) => {
  const { user, logout } = useAuthStore();
  const [name, setName] = useState(user?.name || "");
  
  if (!user) return null;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="glass border-white/10 max-w-md">
        <DialogHeader>
          <DialogTitle className="font-secondary flex items-center gap-2">
            <User className="w-5 h-5 text-primary" /> My Profile
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
              <User className="w-8 h-8 text-primary" />
            </div>
            <div>
              <p className="font-semibold">{user.name || "User"}</p>
              <p className="text-sm text-muted-foreground">{user.email}</p>
              {user.is_pro && <span className="text-xs text-yellow-400 flex items-center gap-1"><Crown className="w-3 h-3" /> Pro Member</span>}
            </div>
          </div>
          
          <div className="glass-light rounded-xl p-4 space-y-3">
            <div>
              <label className="text-xs text-muted-foreground">Email</label>
              <p className="text-sm">{user.email}</p>
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Account Type</label>
              <p className="text-sm">{user.is_pro ? "Pro" : "Free"}</p>
            </div>
          </div>
          
          <Button onClick={() => { logout(); onClose(); }} variant="outline" className="w-full border-red-500/30 text-red-400 hover:bg-red-500/10">
            <LogOut className="w-4 h-4 mr-2" /> Sign Out
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Pro Upgrade Modal with PayPal only
const ProModal = ({ open, onClose }) => {
  const { user, setUser } = useAuthStore();
  const [paypalClientId, setPaypalClientId] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get("/payment/config")
      .then(res => setPaypalClientId(res.data.paypal_client_id))
      .catch(error => {
        console.error("Failed to load payment config:", error);
        // Payment config optional, don't show error toast
      });
  }, []);

  const handlePayPalApprove = async (data) => {
    setLoading(true);
    try {
      const res = await api.post(`/payment/paypal/capture/${data.orderID}`);
      if (res.data.success) {
        setUser({ ...user, is_pro: true });
        toast.success("Pro activated! Enjoy ad-free GAAIUS AI!");
        onClose();
      }
    } catch (error) {
      toast.error("Payment failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="glass border-white/10 max-w-md">
        <DialogHeader>
          <DialogTitle className="font-secondary flex items-center gap-2">
            <Crown className="w-5 h-5 text-yellow-400" /> Upgrade to Pro
          </DialogTitle>
          <DialogDescription>Remove all ads and get unlimited access for just $1/month</DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div className="glass-light rounded-xl p-4">
            <h3 className="font-semibold mb-2">Pro Benefits:</h3>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>✓ No ads - ever!</li>
              <li>✓ Unlimited generations</li>
              <li>✓ Priority generation</li>
              <li>✓ Longer videos (up to 60s)</li>
              <li>✓ HD image exports</li>
              <li>✓ Early access to new features</li>
            </ul>
          </div>
          
          {paypalClientId && (
            <PayPalScriptProvider options={{ clientId: paypalClientId, currency: "USD" }}>
              <PayPalButtons
                style={{ layout: "vertical", color: "gold", shape: "pill" }}
                createOrder={(data, actions) => actions.order.create({
                  purchase_units: [{ amount: { value: "1.00" }, description: "GAAIUS AI Pro - 1 Month" }]
                })}
                onApprove={handlePayPalApprove}
                onError={() => toast.error("PayPal error")}
              />
            </PayPalScriptProvider>
          )}
          
          <p className="text-center text-xs text-muted-foreground">
            Secure payment via PayPal. Cancel anytime.
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Video Ad Modal - Shows after 10 generations or every 30 minutes
const VideoAdModal = ({ open, onClose, onUpgrade }) => {
  const [countdown, setCountdown] = useState(15);
  const [canSkip, setCanSkip] = useState(false);

  useEffect(() => {
    if (open && countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else if (countdown === 0) {
      setCanSkip(true);
    }
  }, [open, countdown]);

  useEffect(() => {
    if (open) {
      setCountdown(15);
      setCanSkip(false);
    }
  }, [open]);

  const adContent = [
    { title: "🚀 GAAIUS AI Pro", subtitle: "Remove all ads for just $1/month", highlight: "Unlimited AI generations!" },
    { title: "⚡ Go Ad-Free", subtitle: "Upgrade to Pro and never see ads again", highlight: "Priority processing!" },
    { title: "🎨 Unlock Full Power", subtitle: "Get Pro for the ultimate AI experience", highlight: "HD exports + longer videos!" }
  ];
  const [ad] = useState(adContent[Math.floor(Math.random() * adContent.length)]);

  return (
    <Dialog open={open} onOpenChange={() => canSkip && onClose()}>
      <DialogContent className="glass border-white/10 max-w-lg" onPointerDownOutside={(e) => !canSkip && e.preventDefault()}>
        <div className="text-center py-6">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center mx-auto mb-4">
            <Crown className="w-10 h-10 text-white" />
          </div>
          <h2 className="text-2xl font-bold mb-2">{ad.title}</h2>
          <p className="text-muted-foreground mb-2">{ad.subtitle}</p>
          <p className="text-yellow-400 font-semibold text-lg mb-6">{ad.highlight}</p>
          
          <div className="space-y-3">
            <Button onClick={onUpgrade} className="w-full bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-black font-semibold">
              <Crown className="w-4 h-4 mr-2" /> Upgrade to Pro - $1/month
            </Button>
            
            {canSkip ? (
              <Button variant="ghost" onClick={onClose} className="w-full text-muted-foreground">
                Skip Ad
              </Button>
            ) : (
              <p className="text-sm text-muted-foreground">
                Skip available in {countdown}s...
              </p>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Ad Component - Only shows for logged out users
const AdBanner = ({ onUpgrade }) => {
  const ads = [
    { text: "🚀 Sign in to unlock all GAAIUS AI features!", cta: "Sign In" },
    { text: "⚡ Create an account for unlimited AI generations!", cta: "Get Started" },
    { text: "🎨 Sign in to save your work and access Pro features!", cta: "Sign In" }
  ];
  const [ad] = useState(ads[Math.floor(Math.random() * ads.length)]);

  return (
    <div className="w-full p-2 glass border-t border-primary/30">
      <div className="max-w-4xl mx-auto flex items-center justify-between">
        <p className="text-xs">{ad.text}</p>
        <Button size="sm" onClick={onUpgrade} className="bg-primary hover:bg-primary/90 text-white text-xs px-2 py-1 h-7">
          {ad.cta}
        </Button>
      </div>
    </div>
  );
};

// Chat Message Component - Removed model labels
const ChatMessage = ({ message, onSpeak }) => {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`} data-testid={`message-${message.id}`}>
      <div className={`max-w-[80%] ${isUser ? "bg-primary/20 border-primary/30 rounded-br-sm" : "bg-secondary/50 border-white/5 rounded-bl-sm"} border rounded-2xl p-4`}>
        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        {!isUser && (
          <button onClick={() => onSpeak(message.content)} className="mt-2 p-1.5 rounded-full hover:bg-white/10" data-testid="speak-button">
            <Volume2 className="w-4 h-4 text-muted-foreground hover:text-white" />
          </button>
        )}
      </div>
    </div>
  );
};

// Generation Result Component - Removed model labels
const GenerationResult = ({ data, type }) => {
  const rawUrl = data.url || data.image_url || data.video_url || data.audio_url || "";
  const url = rawUrl.startsWith("/api") ? `${BACKEND_URL}${rawUrl}` : rawUrl;
  if (!url) return null;

  return (
    <div className="glass rounded-2xl overflow-hidden" data-testid={`result-${data.id}`}>
      {type === "image" && <img src={url} alt={data.prompt} className="w-full h-auto" />}
      {type === "video" && <video src={url} controls className="w-full h-auto bg-black" />}
      {type === "audio" && <audio src={url} controls className="w-full mt-4" />}
      <div className="p-4">
        <p className="text-sm text-muted-foreground line-clamp-2">{data.prompt}</p>
        {type === "file" && data.content && (
          <pre className="mt-2 p-2 bg-black/50 rounded text-xs overflow-auto max-h-40">{data.content}</pre>
        )}
        <a href={url} download target="_blank" rel="noopener noreferrer" className="mt-3 inline-flex items-center gap-2 text-xs text-primary hover:text-primary/80">
          <Download className="w-3 h-3" /> Download
        </a>
      </div>
    </div>
  );
};

// Build Page Component - GAAIUS AI Builder (Full-featured: AI Chat + Image Gen + Live Preview)
const BuildPage = ({ showSidebar = false, navigate, user, showAuth, showPro, showProfile, logout }) => {
  const [prompt, setPrompt] = useState("");
  const [htmlContent, setHtmlContent] = useState(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My App</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * { font-family: 'Inter', sans-serif; }
  </style>
</head>
<body class="bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white min-h-screen">
  <nav class="fixed top-0 w-full bg-black/50 backdrop-blur-xl border-b border-white/10 z-50">
    <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
      <h1 class="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">MyApp</h1>
      <div class="flex gap-4">
        <a href="#" class="text-gray-300 hover:text-white transition">Features</a>
        <a href="#" class="text-gray-300 hover:text-white transition">Pricing</a>
        <button class="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg font-medium transition">Get Started</button>
      </div>
    </div>
  </nav>
  <main class="pt-24 px-6">
    <div class="max-w-4xl mx-auto text-center py-20">
      <h2 class="text-5xl font-bold mb-6 bg-gradient-to-r from-white via-purple-200 to-pink-200 bg-clip-text text-transparent">Build Something Amazing</h2>
      <p class="text-xl text-gray-400 mb-8">Tell GAAIUS AI what you want to build and watch it come to life instantly.</p>
      <button class="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 px-8 py-4 rounded-xl font-semibold text-lg transition transform hover:scale-105">Start Building →</button>
    </div>
  </main>
</body>
</html>`);
  const [loading, setLoading] = useState(false);
  const [imageLoading, setImageLoading] = useState(false);
  const [projectName, setProjectName] = useState("");
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [generatedImages, setGeneratedImages] = useState([]);
  const [activeTab, setActiveTab] = useState("chat");
  const [previewKey, setPreviewKey] = useState(0); // For forcing preview refresh
  const [buildStage, setBuildStage] = useState(null); // Current build stage for staged building
  const nav = useNavigate();
  
  // NEW: Multi-file project support - ENTERPRISE STRUCTURE
  const [projectFiles, setProjectFiles] = useState({
    // Main HTML - Self-contained for preview
    "frontend/index.html": `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GAAIUS Enterprise App</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
  <style>
    * { font-family: 'Inter', system-ui, sans-serif; }
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0a0a0a; }
    ::-webkit-scrollbar-thumb { background: #7c3aed; border-radius: 4px; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    .animate-fade-in { animation: fadeIn 0.6s ease-out; }
  </style>
</head>
<body class="bg-[#0a0a0a] text-white min-h-screen">
  <!-- Navigation -->
  <nav class="fixed top-0 w-full bg-[#0a0a0a]/80 backdrop-blur-xl border-b border-white/10 z-50">
    <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
      <h1 class="text-xl font-bold bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">MyApp</h1>
      <div class="hidden md:flex items-center gap-8">
        <a href="#features" class="text-white/70 hover:text-white transition text-sm">Features</a>
        <a href="#pricing" class="text-white/70 hover:text-white transition text-sm">Pricing</a>
        <a href="#about" class="text-white/70 hover:text-white transition text-sm">About</a>
      </div>
      <button class="bg-violet-600 hover:bg-violet-700 px-4 py-2 rounded-lg font-medium transition text-sm">Get Started</button>
    </div>
  </nav>

  <!-- Hero Section -->
  <section class="pt-32 pb-20 px-6">
    <div class="max-w-5xl mx-auto text-center animate-fade-in">
      <div class="inline-flex items-center gap-2 bg-violet-500/20 border border-violet-500/30 rounded-full px-4 py-1.5 mb-6">
        <i data-lucide="sparkles" class="w-4 h-4 text-violet-400"></i>
        <span class="text-sm text-violet-300">Enterprise-grade Platform</span>
      </div>
      <h1 class="text-5xl md:text-7xl font-bold mb-6 leading-tight">
        <span class="bg-gradient-to-r from-white via-violet-200 to-cyan-200 bg-clip-text text-transparent">Build Something</span><br>
        <span class="bg-gradient-to-r from-violet-400 to-cyan-400 bg-clip-text text-transparent">Amazing</span>
      </h1>
      <p class="text-xl text-white/60 mb-10 max-w-2xl mx-auto leading-relaxed">
        Enterprise-grade application powered by GAAIUS AI Builder. Create stunning apps with production-ready code.
      </p>
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <button class="bg-violet-600 hover:bg-violet-700 px-8 py-4 rounded-xl font-semibold transition text-lg shadow-lg shadow-violet-500/25">
          Get Started <i data-lucide="arrow-right" class="w-5 h-5 inline ml-2"></i>
        </button>
        <button class="bg-white/10 hover:bg-white/20 border border-white/20 px-8 py-4 rounded-xl font-semibold transition text-lg">
          <i data-lucide="play-circle" class="w-5 h-5 inline mr-2"></i> Watch Demo
        </button>
      </div>
    </div>
  </section>

  <!-- Features Section -->
  <section id="features" class="py-20 px-6 bg-[#111]">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-16">
        <h2 class="text-3xl md:text-4xl font-bold mb-4">Powerful Features</h2>
        <p class="text-white/60 max-w-xl mx-auto">Everything you need to build world-class applications</p>
      </div>
      <div class="grid md:grid-cols-3 gap-8">
        <div class="p-8 bg-white/5 border border-white/10 rounded-2xl hover:bg-white/[0.07] transition group">
          <div class="w-12 h-12 bg-violet-500/20 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition">
            <i data-lucide="zap" class="w-6 h-6 text-violet-400"></i>
          </div>
          <h3 class="text-xl font-semibold mb-3">Lightning Fast</h3>
          <p class="text-white/60">Optimized performance with sub-second load times and smooth interactions.</p>
        </div>
        <div class="p-8 bg-white/5 border border-white/10 rounded-2xl hover:bg-white/[0.07] transition group">
          <div class="w-12 h-12 bg-cyan-500/20 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition">
            <i data-lucide="shield-check" class="w-6 h-6 text-cyan-400"></i>
          </div>
          <h3 class="text-xl font-semibold mb-3">Enterprise Security</h3>
          <p class="text-white/60">Bank-grade encryption and security protocols to protect your data.</p>
        </div>
        <div class="p-8 bg-white/5 border border-white/10 rounded-2xl hover:bg-white/[0.07] transition group">
          <div class="w-12 h-12 bg-emerald-500/20 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition">
            <i data-lucide="layers" class="w-6 h-6 text-emerald-400"></i>
          </div>
          <h3 class="text-xl font-semibold mb-3">Scalable Architecture</h3>
          <p class="text-white/60">Built to handle millions of users with auto-scaling infrastructure.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Stats Section -->
  <section class="py-20 px-6">
    <div class="max-w-6xl mx-auto grid md:grid-cols-4 gap-8 text-center">
      <div>
        <p class="text-4xl md:text-5xl font-bold text-violet-400">10K+</p>
        <p class="text-white/60 mt-2">Active Users</p>
      </div>
      <div>
        <p class="text-4xl md:text-5xl font-bold text-cyan-400">99.9%</p>
        <p class="text-white/60 mt-2">Uptime</p>
      </div>
      <div>
        <p class="text-4xl md:text-5xl font-bold text-emerald-400">50+</p>
        <p class="text-white/60 mt-2">Integrations</p>
      </div>
      <div>
        <p class="text-4xl md:text-5xl font-bold text-amber-400">24/7</p>
        <p class="text-white/60 mt-2">Support</p>
      </div>
    </div>
  </section>

  <!-- CTA Section -->
  <section class="py-20 px-6 bg-gradient-to-r from-violet-600/20 to-cyan-600/20 border-y border-white/10">
    <div class="max-w-4xl mx-auto text-center">
      <h2 class="text-3xl md:text-4xl font-bold mb-4">Ready to Get Started?</h2>
      <p class="text-white/60 mb-8 max-w-xl mx-auto">Join thousands of developers building amazing products with GAAIUS.</p>
      <button class="bg-white text-gray-900 hover:bg-gray-100 px-8 py-4 rounded-xl font-semibold transition text-lg">
        Start Building Free <i data-lucide="arrow-right" class="w-5 h-5 inline ml-2"></i>
      </button>
    </div>
  </section>

  <!-- Footer -->
  <footer class="py-12 px-6 border-t border-white/10">
    <div class="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
      <p class="text-white/40 text-sm">© 2025 MyApp. Built with GAAIUS AI Builder.</p>
      <div class="flex gap-6">
        <a href="#" class="text-white/40 hover:text-white transition"><i data-lucide="twitter" class="w-5 h-5"></i></a>
        <a href="#" class="text-white/40 hover:text-white transition"><i data-lucide="github" class="w-5 h-5"></i></a>
        <a href="#" class="text-white/40 hover:text-white transition"><i data-lucide="linkedin" class="w-5 h-5"></i></a>
      </div>
    </div>
  </footer>

  <script>lucide.createIcons();</script>
</body>
</html>`,
    // Source Files - For code reference
    "frontend/src/main.js": `// GAAIUS Enterprise - Main Entry Point
// This file initializes the application

document.addEventListener('DOMContentLoaded', () => {
  console.log('🚀 GAAIUS Enterprise App Starting...');
  initializeApp();
});

function initializeApp() {
  // Initialize icons
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
  
  // Add smooth scroll
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      document.querySelector(this.getAttribute('href')).scrollIntoView({
        behavior: 'smooth'
      });
    });
  });
}`,
    "frontend/src/styles/main.css": `/* GAAIUS Enterprise - Global Styles */

:root {
  --color-primary: #7c3aed;
  --color-secondary: #06b6d4;
  --color-bg: #0a0a0a;
  --color-surface: #111;
  --color-border: rgba(255, 255, 255, 0.1);
}

* {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background: var(--color-bg);
  color: #fff;
  line-height: 1.6;
}

/* Custom Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: var(--color-bg); }
::-webkit-scrollbar-thumb { background: var(--color-primary); border-radius: 4px; }

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-fade-in { animation: fadeIn 0.6s ease-out; }
.animate-pulse { animation: pulse 2s infinite; }

/* Glassmorphism */
.glass {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid var(--color-border);
}`,
    // Backend
    "backend/server.js": `// GAAIUS Enterprise - API Server
const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'healthy', version: '1.0.0', timestamp: new Date().toISOString() });
});

// Routes
app.get('/api/users', (req, res) => {
  res.json({ users: [], total: 0 });
});

app.post('/api/auth/login', (req, res) => {
  const { email, password } = req.body;
  res.json({ success: true, token: 'jwt_token_here' });
});

const PORT = process.env.PORT || 8001;
app.listen(PORT, () => console.log(\`Server running on port \${PORT}\`));`,
    // Config
    "config/app.json": `{
  "name": "GAAIUS Enterprise App",
  "version": "1.0.0",
  "description": "Enterprise-grade application built with GAAIUS AI Builder",
  "author": "GAAIUS AI",
  "features": ["auth", "api", "realtime", "analytics"],
  "theme": "dark",
  "framework": "vanilla"
}`,
    "config/build.json": `{
  "targets": {
    "web": { "enabled": true, "port": 3000 },
    "mobile": { "enabled": false },
    "desktop": { "enabled": false }
  },
  "optimization": {
    "minify": true,
    "treeshake": true
  }
}`,
    // README
    "README.md": `# GAAIUS Enterprise App

Built with GAAIUS AI Builder - Enterprise Architecture

## 📁 Project Structure

\`\`\`
├── frontend/          # Frontend application
│   ├── index.html    # Main entry point
│   └── src/
│       ├── main.js   # JavaScript entry
│       └── styles/   # CSS styles
├── backend/          # API server
│   └── server.js     # Express server
├── config/           # Configuration files
└── README.md
\`\`\`

## 🚀 Getting Started

1. Open the preview to see the app
2. Edit files in the code tab
3. Changes auto-update in preview

## ✨ Features

- Modern dark theme UI
- Responsive design
- Smooth animations
- SEO optimized

---
Generated by GAAIUS AI Builder v2.0
`
  });
  const [activeFile, setActiveFile] = useState("frontend/index.html");
  const [rightPanelTab, setRightPanelTab] = useState("preview"); // preview | code | terminal
  const [terminalOutput, setTerminalOutput] = useState([
    { type: "system", text: "GAAIUS AI Builder Terminal v1.0" },
    { type: "system", text: "Ready for commands..." }
  ]);
  const [isPreviewFullscreen, setIsPreviewFullscreen] = useState(false);
  const [showFileTree, setShowFileTree] = useState(true);
  const [executingCode, setExecutingCode] = useState(false);
  const [currentProject, setCurrentProject] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState("python");

  // Get file language for Monaco
  const getLanguage = (filename) => {
    const ext = filename.split('.').pop();
    const langMap = {
      'html': 'html',
      'css': 'css',
      'js': 'javascript',
      'jsx': 'javascript',
      'ts': 'typescript',
      'tsx': 'typescript',
      'json': 'json',
      'py': 'python',
      'md': 'markdown'
    };
    return langMap[ext] || 'plaintext';
  };

  // Add terminal log
  const addTerminalLog = (type, text) => {
    setTerminalOutput(prev => [...prev, { type, text, timestamp: new Date().toLocaleTimeString() }]);
  };

  // Create new file
  const createNewFile = (filename) => {
    if (projectFiles[filename]) {
      toast.error("File already exists");
      return;
    }
    const ext = filename.split('.').pop();
    let defaultContent = "";
    if (ext === 'html') defaultContent = "<!DOCTYPE html>\n<html>\n<head>\n  <title>New Page</title>\n</head>\n<body>\n  \n</body>\n</html>";
    if (ext === 'css') defaultContent = "/* New stylesheet */\n";
    if (ext === 'js') defaultContent = "// New JavaScript file\n";
    
    setProjectFiles(prev => ({ ...prev, [filename]: defaultContent }));
    setActiveFile(filename);
    addTerminalLog("success", `Created file: ${filename}`);
    toast.success(`Created ${filename}`);
  };

  // Delete file
  const deleteFile = (filename) => {
    if (Object.keys(projectFiles).length <= 1) {
      toast.error("Cannot delete the last file");
      return;
    }
    const newFiles = { ...projectFiles };
    delete newFiles[filename];
    setProjectFiles(newFiles);
    if (activeFile === filename) {
      setActiveFile(Object.keys(newFiles)[0]);
    }
    addTerminalLog("warning", `Deleted file: ${filename}`);
    toast.success(`Deleted ${filename}`);
  };

  // Update file content
  const updateFileContent = (content) => {
    setProjectFiles(prev => ({ ...prev, [activeFile]: content }));
    // Also update htmlContent if it's the main HTML file for preview compatibility
    if (activeFile === "frontend/index.html" || activeFile === "index.html") {
      setHtmlContent(content);
    }
  };

  // Build combined HTML for preview (combines all files - supports enterprise structure)
  const buildPreviewHtml = () => {
    // Get the main HTML file (support both flat and nested structures)
    let html = projectFiles["frontend/index.html"] || projectFiles["index.html"] || htmlContent;
    
    // Inject CSS files
    const cssFiles = Object.keys(projectFiles).filter(f => f.endsWith('.css'));
    cssFiles.forEach(cssFile => {
      if (projectFiles[cssFile]) {
        html = html.replace('</head>', `<style>/* ${cssFile} */\n${projectFiles[cssFile]}</style>\n</head>`);
      }
    });
    
    // Inject JS files (in correct order)
    const jsFiles = Object.keys(projectFiles).filter(f => f.endsWith('.js') && !f.includes('server'));
    jsFiles.forEach(jsFile => {
      if (projectFiles[jsFile]) {
        // Convert ES modules to inline for preview
        let jsContent = projectFiles[jsFile]
          .replace(/import\s+.*from\s+['"].*['"];?\n?/g, '') // Remove imports
          .replace(/export\s+(default\s+)?/g, ''); // Remove exports
        html = html.replace('</body>', `<script>/* ${jsFile} */\n${jsContent}</script>\n</body>`);
      }
    });
    
    return html;
  };

  // Generate image using Pollinations AI (free, no API key needed)
  const generateImage = async (imagePrompt) => {
    setImageLoading(true);
    try {
      const encodedPrompt = encodeURIComponent(imagePrompt);
      const imageUrl = `https://image.pollinations.ai/prompt/${encodedPrompt}?width=512&height=512&nologo=true`;
      
      // Pre-load the image to ensure it's generated
      const img = new window.Image();
      img.onload = () => {
        setGeneratedImages(prev => [{
          id: Date.now(),
          prompt: imagePrompt,
          url: imageUrl,
          timestamp: new Date().toISOString()
        }, ...prev]);
        setChatHistory(prev => [...prev, { 
          role: "assistant", 
          content: `🎨 Image generated! Click to copy the URL and use it in your code.\n\nURL: ${imageUrl}`,
          imageUrl: imageUrl
        }]);
        addTerminalLog("success", "Image generated successfully");
        toast.success("Image generated!");
        setImageLoading(false);
      };
      img.onerror = () => {
        const errorMsg = "Failed to generate image. Please try a different prompt.";
        addTerminalLog("error", errorMsg);
        toast.error(errorMsg);
        setImageLoading(false);
      };
      img.src = imageUrl;
    } catch (error) {
      const errorMsg = error.message || "Image generation failed";
      addTerminalLog("error", errorMsg);
      toast.error("Image generation failed. Please try again.");
      setImageLoading(false);
    }
  };

  // Copy image URL to clipboard
  const copyImageUrl = (url) => {
    navigator.clipboard.writeText(url);
    toast.success("Image URL copied! Paste it in your code.");
  };

  // Insert image into HTML
  const insertImageIntoCode = (url) => {
    const imgTag = `<img src="${url}" alt="Generated image" class="w-full max-w-md mx-auto rounded-lg shadow-lg" />`;
    setHtmlContent(prev => {
      // Insert before </main> or </body>
      if (prev.includes('</main>')) {
        return prev.replace('</main>', `  ${imgTag}\n</main>`);
      }
      return prev.replace('</body>', `  ${imgTag}\n</body>`);
    });
    toast.success("Image inserted into your code!");
  };

  const handleGenerate = async () => {
    if (!prompt.trim() || loading) return;
    
    const promptLower = prompt.toLowerCase();
    
    // Check if user wants to generate an image/logo/icon
    const isImageRequest = promptLower.includes('image') || 
                          promptLower.includes('logo') || 
                          promptLower.includes('icon') ||
                          promptLower.includes('picture') ||
                          promptLower.includes('graphic') ||
                          promptLower.includes('illustration') ||
                          promptLower.includes('banner') ||
                          promptLower.includes('background') ||
                          promptLower.includes('photo') ||
                          promptLower.includes('generate an image') ||
                          promptLower.includes('create an image') ||
                          promptLower.includes('make an image') ||
                          promptLower.includes('design a logo') ||
                          promptLower.includes('create a logo');
    
    setChatHistory(prev => [...prev, { role: "user", content: prompt }]);
    
    if (isImageRequest) {
      // Use Pollinations AI for image generation
      setPrompt("");
      addTerminalLog("info", `Generating image: ${prompt}`);
      await generateImage(prompt);
      return;
    }
    
    // Check if this is a complex app request (YouTube, Spotify, etc.)
    const isComplexApp = promptLower.includes('youtube') || 
                        promptLower.includes('spotify') ||
                        promptLower.includes('netflix') ||
                        promptLower.includes('twitter') ||
                        promptLower.includes('instagram') ||
                        promptLower.includes('amazon') ||
                        promptLower.includes('facebook') ||
                        promptLower.includes('tiktok') ||
                        promptLower.includes('linkedin') ||
                        promptLower.includes('reddit') ||
                        promptLower.includes('discord') ||
                        promptLower.includes('slack') ||
                        promptLower.includes('airbnb') ||
                        promptLower.includes('uber') ||
                        promptLower.includes('like') ||
                        promptLower.includes('clone') ||
                        promptLower.includes('similar to') ||
                        promptLower.includes('build a') ||
                        promptLower.includes('create a') ||
                        promptLower.includes('make a') ||
                        promptLower.includes('app') ||
                        promptLower.includes('website') ||
                        promptLower.includes('platform') ||
                        promptLower.includes('dashboard') ||
                        promptLower.includes('e-commerce') ||
                        promptLower.includes('ecommerce') ||
                        promptLower.includes('shop') ||
                        promptLower.includes('store') ||
                        promptLower.includes('blog') ||
                        promptLower.includes('portfolio') ||
                        promptLower.includes('landing page');
    
    // AUTO-SAVE: Generate unique project name from prompt
    const generateProjectName = () => {
      const keywords = prompt.toLowerCase().match(/\b(youtube|spotify|netflix|twitter|instagram|amazon|dashboard|blog|portfolio|shop|store|app|website|clone)\b/);
      const mainKeyword = keywords ? keywords[0] : 'project';
      const timestamp = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }).replace(':', '');
      return `${mainKeyword.charAt(0).toUpperCase() + mainKeyword.slice(1)}_${timestamp}`;
    };
    
    // Use Groq for code generation
    setLoading(true);
    
    if (isComplexApp) {
      addTerminalLog("info", `🚀 GAAIUS PROJECT RUNTIME: Analyzing "${prompt}"`);
      addTerminalLog("info", `📋 Generating full-stack enterprise scaffold...`);
      setChatHistory(prev => [...prev, { role: "assistant", content: "🚀 **GAAIUS PROJECT RUNTIME Active**\n\n1️⃣ Analyzing your request...\n2️⃣ Creating enterprise blueprint...\n3️⃣ Generating full-stack project scaffold...\n4️⃣ Building React + TypeScript frontend...\n5️⃣ Building Express + TypeScript backend...\n6️⃣ Setting up services & components..." }]);
    } else {
      addTerminalLog("info", `AI generating code for: ${prompt}`);
    }
    
    try {
      // Determine if this is an iterative build (existing files present)
      const hasExistingProject = Object.keys(projectFiles).length > 5;
      
      if (isComplexApp) {
        // Use GAAIUS PROJECT RUNTIME for complex apps - generates full project scaffold
        const res = await api.post("/build/generate-runtime", { 
          prompt,
          existing_files: hasExistingProject ? projectFiles : {},
          is_iterative: hasExistingProject
        }, { timeout: 180000 }); // 3 minute timeout for full projects
        
        if (res.data.success && res.data.project_files) {
          const appName = res.data.blueprint?.app_name || generateProjectName();
          const stats = res.data.stats || {};
          const runCommands = res.data.run_commands || {};
          
          // Update project files with the full scaffold
          setProjectFiles(res.data.project_files);
          
          // Set active file to the main dashboard
          if (res.data.project_files["frontend/src/pages/Dashboard.tsx"]) {
            setActiveFile("frontend/src/pages/Dashboard.tsx");
          } else if (res.data.project_files["frontend/index.html"]) {
            setActiveFile("frontend/index.html");
          }
          
          // Update HTML content for preview (if index.html exists)
          if (res.data.project_files["frontend/index.html"]) {
            setHtmlContent(res.data.project_files["frontend/index.html"]);
          }
          
          // Refresh preview to show the new content
          setPreviewKey(prev => prev + 1);
          
          // Show code first, then switch to preview after a short delay
          setRightPanelTab("code");
          setTimeout(() => {
            setRightPanelTab("preview");
            setPreviewKey(prev => prev + 1);
          }, 1500);
          
          // Log stats to terminal
          addTerminalLog("success", `✅ ${appName} - Enterprise Project Generated!`);
          addTerminalLog("info", `📁 Total Files: ${stats.total_files || 0}`);
          addTerminalLog("info", `📄 Total Lines: ${(stats.total_lines || 0).toLocaleString()}`);
          addTerminalLog("info", `🎨 Frontend: ${stats.frontend_files || 0} files (React + Vite + TypeScript)`);
          addTerminalLog("info", `⚙️ Backend: ${stats.backend_files || 0} files (Express + TypeScript)`);
          addTerminalLog("info", `📦 Shared: ${stats.shared_files || 0} files`);
          addTerminalLog("info", `🐳 DevOps: ${stats.devops_files || 0} files (Docker, Shell scripts)`);
          
          // Log run commands
          if (runCommands.quick_start) {
            addTerminalLog("success", `🚀 Quick Start: ${runCommands.quick_start}`);
          }
          
          const features = res.data.blueprint?.features?.join(", ") || "Full-stack app";
          
          setChatHistory(prev => [...prev, { 
            role: "assistant", 
            content: `✅ **${appName}** - Enterprise Project Ready!\n\n📊 **Project Stats:**\n• ${stats.total_files || 0} files generated\n• ${(stats.total_lines || 0).toLocaleString()} lines of code\n• Frontend: React + Vite + TypeScript\n• Backend: Express + TypeScript + MongoDB\n\n🔧 **Features:** ${features}\n\n📁 **Structure:**\n• frontend/ - React app with components, pages, services\n• backend/ - Express API with auth, routes, models\n• shared/ - Common types and utilities\n• config/ - App configuration\n• docker/ - Docker configuration\n\n🚀 **Run Locally:**\n• Quick: \`make dev\`\n• With Docker: \`docker-compose up\`\n• Manual: \`cd frontend && npm install && npm run dev\`\n\n💡 **Next Steps:**\n1. Browse the code in the file explorer\n2. Click any file to view/edit\n3. Use "Refresh" to update preview\n4. Export when ready!\n\n📱 **Export Options:** Web, Desktop (Electron), Mobile (Capacitor), Docker` 
          }]);
          
          toast.success(`${appName} generated with ${stats.total_files} files!`);
        }
      } else {
        // Use legacy endpoint for simple requests (single HTML file)
        const res = await api.post("/build/generate", { 
          prompt, 
          current_code: projectFiles["frontend/index.html"] || projectFiles["index.html"] || htmlContent 
        }, { timeout: 120000 });
        
        if (res.data.code) {
          const autoName = res.data.blueprint?.app_name || generateProjectName();
          setProjectFiles(prev => ({ ...prev, "frontend/index.html": res.data.code }));
          setHtmlContent(res.data.code);
          setActiveFile("frontend/index.html");
          setRightPanelTab("preview");
          setPreviewKey(prev => prev + 1); // Refresh preview
          
          const qualityEmoji = res.data.quality_score >= 80 ? "🟢" : res.data.quality_score >= 60 ? "🟡" : "🔴";
          const templateInfo = res.data.blueprint?.template ? `📋 Template: ${res.data.blueprint.template}` : "";
          
          addTerminalLog("info", `${qualityEmoji} Quality Score: ${res.data.quality_score || 75}/100`);
          if (res.data.quality_checks?.length > 0) {
            addTerminalLog("success", `✓ Checks passed: ${res.data.quality_checks.join(", ")}`);
          }
          
          setChatHistory(prev => [...prev, { role: "assistant", content: `✅ Done! Quality: ${res.data.quality_score || 75}/100 ${templateInfo}` }]);
          addTerminalLog("success", `Code generated and saved to frontend/index.html`);
          toast.success("Code updated!");
        }
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || "Unknown error";
      const userMessage = error.response?.status === 401 
        ? "Please log in to generate code" 
        : error.response?.status === 429 
        ? "Rate limit exceeded. Please wait before trying again" 
        : error.response?.status === 500
        ? "Server error. Please try again shortly"
        : "Generation failed. Please try again with more specific details";
      
      setChatHistory(prev => [...prev, { role: "assistant", content: `❌ ${userMessage}` }]);
      addTerminalLog("error", `Generation failed: ${errorMsg}`);
      toast.error(userMessage);
    } finally {
      setLoading(false);
      setPrompt("");
    }
  };

  const handleSaveToProject = async () => {
    if (!projectName.trim()) return;
    try {
      addTerminalLog("info", `Saving project: ${projectName}`);
      const res = await api.post("/projects", { name: projectName, description: "Created from AI Builder", type: "web" });
      await api.put(`/projects/${res.data.id}/files`, projectFiles);
      addTerminalLog("success", `Project saved with ${Object.keys(projectFiles).length} files`);
      toast.success("Saved to project!");
      setShowSaveDialog(false);
      (navigate || nav)("/projects");
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.message || "Unknown error";
      addTerminalLog("error", `Save failed: ${errorMsg}`);
      const userMessage = error.response?.status === 401
        ? "Please log in to save projects"
        : error.response?.status === 409
        ? "Project name already exists"
        : "Failed to save project";
      toast.error(userMessage);
    }
  };

  const [showExportMenu, setShowExportMenu] = useState(false);
  
  const downloadProject = (format = 'web') => {
    const combinedHtml = buildPreviewHtml();
    const timestamp = new Date().toISOString().slice(0, 10);
    
    if (format === 'web') {
      // Standard HTML download
      const blob = new Blob([combinedHtml], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `gaaius_app_${timestamp}.html`;
      a.click();
      URL.revokeObjectURL(url);
      addTerminalLog("success", "Web app downloaded as HTML");
      toast.success("Web app downloaded!");
    } else if (format === 'electron') {
      // Export as Electron-ready project
      const electronPackage = JSON.stringify({
        name: "gaaius-app",
        version: "1.0.0",
        main: "main.js",
        scripts: { start: "electron ." }
      }, null, 2);
      
      const electronMain = `const { app, BrowserWindow } = require('electron');
function createWindow() {
  const win = new BrowserWindow({ width: 1200, height: 800, webPreferences: { nodeIntegration: true }});
  win.loadFile('index.html');
}
app.whenReady().then(createWindow);`;
      
      const blob = new Blob([`<!-- ELECTRON PROJECT -->\n<!-- 1. Install: npm init -y && npm i electron --save-dev -->\n<!-- 2. Create main.js with electron config -->\n<!-- 3. Run: npx electron . -->\n\n${combinedHtml}`], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `gaaius_electron_${timestamp}.html`;
      a.click();
      URL.revokeObjectURL(url);
      addTerminalLog("success", "Electron app package created");
      toast.success("Electron package ready! See instructions in file.");
    } else if (format === 'capacitor') {
      // Export as Capacitor-ready for Android/iOS
      const capacitorInstructions = `<!--
CAPACITOR PROJECT - Build for Android & iOS

Steps:
1. Create new project: npm init vite@latest my-app
2. Copy this HTML content to src/index.html
3. Install Capacitor: npm i @capacitor/core @capacitor/cli
4. Initialize: npx cap init
5. Add platforms:
   - Android: npx cap add android
   - iOS: npx cap add ios
6. Build: npm run build
7. Sync: npx cap sync
8. Open in IDE:
   - Android: npx cap open android
   - iOS: npx cap open ios

For Google Play / App Store submission:
- Android: Use Android Studio to build APK/AAB
- iOS: Use Xcode to archive and upload
-->

${combinedHtml}`;
      
      const blob = new Blob([capacitorInstructions], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `gaaius_mobile_${timestamp}.html`;
      a.click();
      URL.revokeObjectURL(url);
      addTerminalLog("success", "Mobile app package created (Android/iOS)");
      toast.success("Mobile package ready! See instructions in file.");
    }
    setShowExportMenu(false);
  };

  // Execute code using Build Service API
  const handleExecuteCode = async (code, language) => {
    setExecutingCode(true);
    addTerminalLog("info", `Executing ${language} code...`);
    try {
      // Create temp project if needed
      if (!currentProject) {
        const projRes = await api.post("/api/build/project/create", {
          name: `temp-${Date.now()}`,
          template: language === "python" ? "python" : "javascript"
        });
        setCurrentProject(projRes.data);
      }

      // Execute code
      const execRes = await api.post(
        `/api/build/project/${currentProject?.id || projRes.data.id}/execute`,
        { code, language, timeout: 30 }
      );

      if (execRes.data.error) {
        addTerminalLog("error", `❌ ${execRes.data.error}`);
        toast.error("Execution error");
      } else {
        addTerminalLog("success", execRes.data.output || "Code executed successfully");
        toast.success("Code executed!");
      }
    } catch (error) {
      const msg = error.response?.data?.detail || error.message || "Execution failed";
      addTerminalLog("error", msg);
      toast.error(msg);
    } finally {
      setExecutingCode(false);
    }
  };

  // Install package
  const handleInstallPackage = async (pkg, language) => {
    addTerminalLog("info", `Installing ${pkg} (${language})...`);
    try {
      if (!currentProject) {
        const projRes = await api.post("/api/build/project/create", {
          name: `temp-${Date.now()}`,
          template: language === "python" ? "python" : "javascript"
        });
        setCurrentProject(projRes.data);
      }

      const res = await api.post(
        `/api/build/project/${currentProject?.id}/package/install`,
        { package: pkg, language }
      );

      if (res.data.success) {
        addTerminalLog("success", `✅ Installed ${pkg}`);
        toast.success(`${pkg} installed!`);
      } else {
        addTerminalLog("error", `Failed: ${res.data.output}`);
        toast.error("Installation failed");
      }
    } catch (error) {
      const msg = error.response?.data?.detail || error.message || "Installation failed";
      addTerminalLog("error", msg);
      toast.error(msg);
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#0a0a0a]">
      <Dialog open={showSaveDialog} onOpenChange={setShowSaveDialog}>
        <DialogContent className="glass border-white/10">
          <DialogHeader><DialogTitle>Save to Project</DialogTitle></DialogHeader>
          <Input value={projectName} onChange={(e) => setProjectName(e.target.value)} placeholder="Project name..." className="bg-white/5 border-white/10" />
          <Button onClick={handleSaveToProject} className="w-full bg-primary">Save</Button>
        </DialogContent>
      </Dialog>
      
      {/* Header */}
      <div className="h-12 border-b border-white/10 flex items-center justify-between px-4 bg-[#111]">
        <div className="flex items-center gap-3">
          <Button size="sm" variant="ghost" onClick={() => (navigate || nav)("/")} className="h-7 text-xs">
            <X className="w-3 h-3 mr-1" /> Exit
          </Button>
          <div className="h-4 w-px bg-white/20" />
          <h2 className="font-secondary text-sm font-bold flex items-center gap-2">
            <Hammer className="w-4 h-4 text-orange-400" /> GAAIUS AI Builder
          </h2>
        </div>
        <div className="flex items-center gap-2 relative">
          <Button size="sm" onClick={() => setShowExportMenu(!showExportMenu)} variant="outline" className="h-7 text-xs">
            <Download className="w-3 h-3 mr-1" /> Export ▾
          </Button>
          {showExportMenu && (
            <div className="absolute top-full right-16 mt-1 bg-[#1a1a1a] border border-white/10 rounded-lg shadow-xl z-50 min-w-[180px]">
              <button onClick={() => downloadProject('web')} className="w-full px-3 py-2 text-left text-xs hover:bg-white/5 flex items-center gap-2">
                🌐 Web (HTML/CSS/JS)
              </button>
              <button onClick={() => downloadProject('electron')} className="w-full px-3 py-2 text-left text-xs hover:bg-white/5 flex items-center gap-2">
                💻 Desktop (Electron/EXE)
              </button>
              <button onClick={() => downloadProject('capacitor')} className="w-full px-3 py-2 text-left text-xs hover:bg-white/5 flex items-center gap-2">
                📱 Android/iOS (Capacitor)
              </button>
            </div>
          )}
          <Button size="sm" onClick={() => setShowSaveDialog(true)} variant="default" className="h-7 text-xs bg-primary">
            <Save className="w-3 h-3 mr-1" /> Save
          </Button>
        </div>
      </div>
      
      <div className="flex-1 flex overflow-hidden">
        {/* Left: AI Chat + Images Panel */}
        <div className="w-96 border-r border-white/10 flex flex-col bg-[#0d0d0d]">
          {/* Tabs */}
          <div className="border-b border-white/10">
            <div className="flex">
              <button 
                onClick={() => setActiveTab("chat")}
                className={`flex-1 p-3 text-sm font-medium transition ${activeTab === "chat" ? "bg-orange-500/20 text-orange-400 border-b-2 border-orange-400" : "text-muted-foreground hover:bg-white/5"}`}
              >
                <Sparkles className="w-4 h-4 inline mr-2" />Build
              </button>
              <button 
                onClick={() => setActiveTab("images")}
                className={`flex-1 p-3 text-sm font-medium transition ${activeTab === "images" ? "bg-cyan-500/20 text-cyan-400 border-b-2 border-cyan-400" : "text-muted-foreground hover:bg-white/5"}`}
              >
                <Image className="w-4 h-4 inline mr-2" />Images ({generatedImages.length})
              </button>
              <button 
                onClick={() => setActiveTab("files")}
                className={`flex-1 p-3 text-sm font-medium transition ${activeTab === "files" ? "bg-green-500/20 text-green-400 border-b-2 border-green-400" : "text-muted-foreground hover:bg-white/5"}`}
              >
                <FileCode className="w-4 h-4 inline mr-2" />Files
              </button>
            </div>
          </div>

          {activeTab === "files" ? (
            <FileExplorer 
              files={projectFiles}
              activeFile={activeFile}
              onSelectFile={setActiveFile}
              onCreateFile={createNewFile}
              onDeleteFile={deleteFile}
            />
          ) : activeTab === "chat" ? (
            <>
              <div className="p-4 border-b border-white/10">
                <p className="text-xs text-muted-foreground">
                  🚀 <strong>Build apps</strong>: "Create YouTube clone"<br/>
                  🎨 <strong>Generate images</strong>: "Create a logo for..."
                </p>
              </div>
              
              <ScrollArea className="flex-1 p-4">
                {chatHistory.length === 0 ? (
                  <div className="text-center py-6">
                    <Hammer className="w-12 h-12 text-orange-400/50 mx-auto mb-4" />
                    <p className="text-sm text-muted-foreground mb-4">Build ANY app or website</p>
                    
                    {/* Quick Templates */}
                    <div className="mb-4 p-3 bg-violet-500/10 border border-violet-500/20 rounded-xl">
                      <p className="text-xs text-violet-400 font-semibold mb-2">📋 Quick Templates</p>
                      <div className="grid grid-cols-2 gap-2">
                        <button onClick={() => setPrompt("Build a SaaS dashboard with stats, charts, and user management")} className="text-xs p-2 bg-white/5 hover:bg-white/10 rounded-lg text-left transition">📊 Dashboard</button>
                        <button onClick={() => setPrompt("Create an e-commerce store with products, cart, and checkout")} className="text-xs p-2 bg-white/5 hover:bg-white/10 rounded-lg text-left transition">🛒 E-commerce</button>
                        <button onClick={() => setPrompt("Build an AI chat interface with sidebar and message history")} className="text-xs p-2 bg-white/5 hover:bg-white/10 rounded-lg text-left transition">🤖 AI Chat</button>
                        <button onClick={() => setPrompt("Create a crypto portfolio tracker with assets and charts")} className="text-xs p-2 bg-white/5 hover:bg-white/10 rounded-lg text-left transition">💰 Crypto App</button>
                        <button onClick={() => setPrompt("Build an admin panel with content management and user roles")} className="text-xs p-2 bg-white/5 hover:bg-white/10 rounded-lg text-left transition">⚙️ Admin Panel</button>
                        <button onClick={() => setPrompt("Create a modern landing page for a startup")} className="text-xs p-2 bg-white/5 hover:bg-white/10 rounded-lg text-left transition">🚀 Landing Page</button>
                      </div>
                    </div>
                    
                    <div className="space-y-2 text-xs text-left">
                      <p className="text-orange-400/70 cursor-pointer hover:text-orange-400 p-2 rounded hover:bg-white/5" onClick={() => setPrompt("Build a YouTube clone with video grid, sidebar, and search")}>🎬 "Build a YouTube clone"</p>
                      <p className="text-orange-400/70 cursor-pointer hover:text-orange-400 p-2 rounded hover:bg-white/5" onClick={() => setPrompt("Create a Spotify-like music player with playlists and player controls")}>🎵 "Create a Spotify clone"</p>
                      <p className="text-orange-400/70 cursor-pointer hover:text-orange-400 p-2 rounded hover:bg-white/5" onClick={() => setPrompt("Build a Netflix homepage with hero banner and content rows")}>📺 "Build a Netflix homepage"</p>
                      <p className="text-orange-400/70 cursor-pointer hover:text-orange-400 p-2 rounded hover:bg-white/5" onClick={() => setPrompt("Create a Twitter/X feed with tweets, sidebar, and compose box")}>🐦 "Create a Twitter clone"</p>
                      <p className="text-orange-400/70 cursor-pointer hover:text-orange-400 p-2 rounded hover:bg-white/5" onClick={() => setPrompt("Build an Instagram profile page with photo grid and stories")}>📸 "Build Instagram UI"</p>
                      <p className="text-orange-400/70 cursor-pointer hover:text-orange-400 p-2 rounded hover:bg-white/5" onClick={() => setPrompt("Create an Amazon-like e-commerce store with product grid and cart")}>🛒 "Create Amazon store"</p>
                      <p className="text-cyan-400/70 cursor-pointer hover:text-cyan-400 p-2 rounded hover:bg-white/5" onClick={() => setPrompt("Create a professional logo for a tech startup")}>🎨 "Create a logo"</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-5" style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif' }}>
                    {chatHistory.map((msg, i) => (
                      <div key={i} className={`rounded-xl text-sm ${msg.role === "user" ? "bg-orange-500/10 border border-orange-500/20 p-4 ml-6" : "bg-transparent"}`} style={{ marginBottom: '20px' }}>
                        <div className="flex items-center gap-2 mb-3">
                          <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold ${msg.role === "user" ? "bg-orange-500" : "bg-gradient-to-br from-violet-500 to-cyan-500"}`}>
                            {msg.role === "user" ? "U" : "G"}
                          </div>
                          <span className="text-sm font-medium text-white/80">{msg.role === "user" ? "You" : "GAAIUS AI"}</span>
                        </div>
                        <div className="pl-9" style={{ lineHeight: '1.6' }}>
                          {/* ChatGPT-style paragraph and bullet rendering */}
                          {msg.content.split('\n\n').map((paragraph, pIdx) => (
                            <div key={pIdx} style={{ marginBottom: '16px' }}>
                              {paragraph.split('\n').map((line, lIdx) => {
                                // Check if it's a bullet point
                                const isBullet = line.startsWith('•') || line.startsWith('-') || line.startsWith('*') || line.match(/^\d+\./);
                                const isBold = line.startsWith('**') && line.endsWith('**');
                                
                                return (
                                  <p key={lIdx} style={{ 
                                    marginBottom: isBullet ? '8px' : '4px', 
                                    paddingLeft: isBullet ? '20px' : '0',
                                    lineHeight: '1.6'
                                  }}>
                                    {isBold ? (
                                      <strong className="text-white font-semibold">{line.replace(/\*\*/g, '')}</strong>
                                    ) : line}
                                  </p>
                                );
                              })}
                            </div>
                          ))}
                        </div>
                        {msg.imageUrl && (
                          <div className="mt-3 pl-9">
                            <img src={msg.imageUrl} alt="Generated" className="w-full rounded-lg border border-white/10" />
                            <div className="flex gap-2 mt-2">
                              <Button size="sm" variant="outline" onClick={() => copyImageUrl(msg.imageUrl)} className="text-xs h-7 flex-1">
                                Copy URL
                              </Button>
                              <Button size="sm" variant="outline" onClick={() => insertImageIntoCode(msg.imageUrl)} className="text-xs h-7 flex-1 bg-cyan-500/20 text-cyan-400 border-cyan-500/30">
                                Insert to Code
                              </Button>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea>
            </>
          ) : (
            <ScrollArea className="flex-1 p-4">
              {generatedImages.length === 0 ? (
                <div className="text-center py-8">
                  <Image className="w-12 h-12 text-cyan-400/50 mx-auto mb-4" />
                  <p className="text-sm text-muted-foreground mb-2">No images generated yet</p>
                  <p className="text-xs text-muted-foreground">Ask AI to "create a logo" or "generate an image"</p>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-2">
                  {generatedImages.map((img) => (
                    <div key={img.id} className="relative group">
                      <img src={img.url} alt={img.prompt} className="w-full rounded-lg border border-white/10" />
                      <div className="absolute inset-0 bg-black/70 opacity-0 group-hover:opacity-100 transition flex flex-col items-center justify-center p-2 rounded-lg">
                        <p className="text-xs text-center mb-2 line-clamp-2">{img.prompt}</p>
                        <div className="flex gap-1">
                          <Button size="sm" variant="ghost" onClick={() => copyImageUrl(img.url)} className="text-xs h-6 px-2">
                            Copy
                          </Button>
                          <Button size="sm" variant="ghost" onClick={() => insertImageIntoCode(img.url)} className="text-xs h-6 px-2 text-cyan-400">
                            Insert
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          )}
          
          <div className="p-4 border-t border-white/10">
            <div className="flex gap-3">
              <Input
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Build website or generate image..."
                className="flex-1 bg-white/5 border-white/10 h-11 text-sm px-4"
                style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}
                onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
              />
              <Button onClick={handleGenerate} disabled={loading || imageLoading} className="bg-orange-500 hover:bg-orange-600 h-11 px-5">
                {(loading || imageLoading) ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </Button>
            </div>
          </div>
        </div>
        
        {/* Middle: File Tree (collapsible) - Enterprise Structure */}
        {showFileTree && (
          <div className="w-52 border-r border-white/10 bg-[#0d0d0d] flex flex-col">
            <div className="p-2 border-b border-white/10 flex items-center justify-between">
              <span className="text-xs font-mono text-muted-foreground uppercase">Explorer</span>
              <Button 
                size="sm" 
                variant="ghost" 
                className="h-5 w-5 p-0"
                onClick={() => {
                  const name = window.prompt("New file path (e.g., frontend/src/pages/home.js):");
                  if (name) createNewFile(name);
                }}
              >
                <Plus className="w-3 h-3" />
              </Button>
            </div>
            <ScrollArea className="flex-1">
              <div className="p-1">
                {/* Group files by folder */}
                {(() => {
                  const folders = {};
                  Object.keys(projectFiles).forEach(filepath => {
                    const parts = filepath.split('/');
                    if (parts.length > 1) {
                      const folder = parts.slice(0, -1).join('/');
                      if (!folders[folder]) folders[folder] = [];
                      folders[folder].push(filepath);
                    } else {
                      if (!folders['root']) folders['root'] = [];
                      folders['root'].push(filepath);
                    }
                  });
                  
                  return Object.entries(folders).sort().map(([folder, files]) => (
                    <div key={folder} className="mb-1">
                      {folder !== 'root' && (
                        <div className="flex items-center gap-1 p-1 text-[10px] font-mono text-white/50 uppercase">
                          <Folder className="w-3 h-3 text-yellow-500/70" />
                          <span>{folder}</span>
                        </div>
                      )}
                      <div className={folder !== 'root' ? 'pl-3' : ''}>
                        {files.sort().map(filepath => {
                          const filename = filepath.split('/').pop();
                          const ext = filename.split('.').pop();
                          const iconColor = ext === 'html' ? 'text-orange-400' : ext === 'css' ? 'text-blue-400' : ext === 'js' ? 'text-yellow-400' : ext === 'json' ? 'text-green-400' : 'text-white/50';
                          return (
                            <div 
                              key={filepath}
                              className={`flex items-center gap-1.5 p-1 rounded text-[11px] cursor-pointer group ${activeFile === filepath ? "bg-orange-500/20 text-orange-400" : "hover:bg-white/5"}`}
                              onClick={() => setActiveFile(filepath)}
                            >
                              <File className={`w-3 h-3 flex-shrink-0 ${iconColor}`} />
                              <span className="truncate flex-1">{filename}</span>
                              {Object.keys(projectFiles).length > 1 && (
                                <button 
                                  className="opacity-0 group-hover:opacity-100 hover:text-red-400 transition"
                                  onClick={(e) => { e.stopPropagation(); deleteFile(filepath); }}
                                >
                                  <Trash2 className="w-2.5 h-2.5" />
                                </button>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ));
                })()}
              </div>
            </ScrollArea>
          </div>
        )}
        
        {/* Right: Preview / Code / Terminal */}
        <div className="flex-1 flex flex-col">
          {/* Right Panel Tabs */}
          <div className="h-10 border-b border-white/10 flex items-center justify-between px-2 bg-[#111]">
            <div className="flex">
              <button 
                onClick={() => setRightPanelTab("preview")}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium transition ${rightPanelTab === "preview" ? "bg-cyan-500/20 text-cyan-400" : "text-muted-foreground hover:bg-white/5"}`}
              >
                <Eye className="w-3.5 h-3.5" /> Preview
              </button>
              <button 
                onClick={() => setRightPanelTab("code")}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium transition ${rightPanelTab === "code" ? "bg-green-500/20 text-green-400" : "text-muted-foreground hover:bg-white/5"}`}
              >
                <Code className="w-3.5 h-3.5" /> Code
              </button>
              <button 
                onClick={() => setRightPanelTab("terminal")}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium transition ${rightPanelTab === "terminal" ? "bg-purple-500/20 text-purple-400" : "text-muted-foreground hover:bg-white/5"}`}
              >
                <Terminal className="w-3.5 h-3.5" /> Terminal
              </button>
              <button 
                onClick={() => setRightPanelTab("execute")}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium transition ${rightPanelTab === "execute" ? "bg-green-500/20 text-green-400" : "text-muted-foreground hover:bg-white/5"}`}
              >
                <Play className="w-3.5 h-3.5" /> Execute
              </button>
              <button 
                onClick={() => setRightPanelTab("packages")}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium transition ${rightPanelTab === "packages" ? "bg-blue-500/20 text-blue-400" : "text-muted-foreground hover:bg-white/5"}`}
              >
                <Package className="w-3.5 h-3.5" /> Packages
              </button>
            </div>
            {rightPanelTab === "preview" && (
              <button
                onClick={() => setIsPreviewFullscreen(true)}
                className="bg-black/70 hover:bg-black/90 text-white p-2 rounded-lg transition-all shadow-lg"
                title="Enter fullscreen preview"
                data-testid="fullscreen-preview-btn"
              >
                <Maximize2 className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Right Panel Content */}
          {rightPanelTab === "execute" && (
            <CodeExecutionPanel 
              onExecute={handleExecuteCode}
              language={selectedLanguage}
              isLoading={executingCode}
            />
          )}

          {rightPanelTab === "packages" && (
            <PackageManagerPanel 
              language={selectedLanguage}
              onInstall={handleInstallPackage}
              isLoading={executingCode}
            />
          )}

          {rightPanelTab === "terminal" && (
            <TerminalPanel 
              output={terminalOutput}
              isLoading={executingCode}
            />
          )}

          {rightPanelTab === "preview" && (
            <div className="h-full bg-white relative">
              {/* Preview controls */}
              <div className="absolute top-2 right-2 z-10 flex gap-2">
                {/* Refresh button */}
                <button
                  onClick={() => {
                    setPreviewKey(prev => prev + 1);
                    addTerminalLog("info", "🔄 Preview refreshed");
                  }}
                  className="bg-black/70 hover:bg-black/90 text-white p-2 rounded-lg transition-all shadow-lg"
                  title="Refresh preview"
                  data-testid="refresh-preview-btn"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
                {/* Fullscreen button */}
                <button
                  onClick={() => setIsPreviewFullscreen(true)}
                  className="bg-black/70 hover:bg-black/90 text-white p-2 rounded-lg transition-all shadow-lg"
                  title="Enter fullscreen preview"
                  data-testid="fullscreen-preview-btn"
                >
                  <Maximize2 className="w-4 h-4" />
                </button>
              </div>
              <iframe
                key={previewKey}
                srcDoc={buildPreviewHtml()}
                className="w-full h-full border-0"
                title="Preview"
                sandbox="allow-scripts allow-same-origin"
              />
            </div>
          )}

          {rightPanelTab === "code" && (
              <div className="h-full flex flex-col">
                <div className="h-8 bg-[#1e1e1e] border-b border-white/10 flex items-center px-2">
                  <span className="text-xs font-mono text-muted-foreground">{activeFile}</span>
                </div>
                <Editor
                  height="100%"
                  language={getLanguage(activeFile)}
                  value={projectFiles[activeFile] || ""}
                  onChange={(value) => updateFileContent(value || "")}
                  theme="vs-dark"
                  options={{
                    minimap: { enabled: false },
                    fontSize: 13,
                    lineNumbers: "on",
                    scrollBeyondLastLine: false,
                    automaticLayout: true,
                    tabSize: 2,
                    wordWrap: "on"
                  }}
                />
              </div>
            )}
            
            {rightPanelTab === "terminal" && (
              <div className="h-full bg-[#0d0d0d] font-mono text-xs p-3 overflow-auto">
                {terminalOutput.map((log, i) => (
                  <div key={i} className={`py-0.5 ${
                    log.type === "error" ? "text-red-400" : 
                    log.type === "success" ? "text-green-400" : 
                    log.type === "warning" ? "text-yellow-400" :
                    log.type === "info" ? "text-cyan-400" : "text-gray-400"
                  }`}>
                    <span className="text-gray-500">{log.timestamp || ""}</span> {log.text}
                  </div>
                ))}
                <div className="flex items-center mt-2 text-green-400">
                  <ChevronRight className="w-3 h-3 mr-1" />
                  <span className="animate-pulse">_</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
  );
};

// Projects Page Component
const ProjectsPage = () => {
  const [projects, setProjects] = useState([]);
  const [newName, setNewName] = useState("");
  const [selectedProject, setSelectedProject] = useState(null);
  const { user } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) api.get("/projects").then(res => setProjects(res.data)).catch(() => {});
  }, [user]);

  const createProject = async () => {
    if (!newName.trim()) {
      toast.error("Please enter a project name");
      return;
    }
    try {
      const res = await api.post("/projects", { name: newName, description: "", type: "web" });
      if (res.data && res.data.id) {
        setProjects(prev => [res.data, ...prev]);
        setNewName("");
        toast.success("Project created!");
      } else {
        throw new Error("Invalid response");
      }
    } catch (error) {
      console.error("Project creation error:", error);
      toast.error(error.response?.data?.detail || "Failed to create project");
    }
  };

  const openProject = (project) => {
    setSelectedProject(project);
  };

  if (!user) return (
    <div className="h-full flex items-center justify-center">
      <p className="text-muted-foreground">Please sign in to view projects</p>
    </div>
  );

  if (selectedProject) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="flex items-center gap-4 mb-6">
          <Button variant="ghost" onClick={() => setSelectedProject(null)}>&larr; Back</Button>
          <h1 className="font-secondary text-2xl font-bold">{selectedProject.name}</h1>
        </div>
        
        <div className="glass rounded-xl p-6 space-y-4">
          <p className="text-muted-foreground">{selectedProject.description || "No description"}</p>
          <p className="text-xs text-muted-foreground">Created: {new Date(selectedProject.created_at).toLocaleDateString()}</p>
          
          {selectedProject.files && Object.keys(selectedProject.files).length > 0 ? (
            <div className="space-y-2">
              <h3 className="font-semibold">Files:</h3>
              {Object.entries(selectedProject.files).map(([name, content]) => (
                <div key={name} className="glass-light rounded-lg p-3">
                  <p className="text-sm font-mono">{name}</p>
                  <pre className="mt-2 text-xs overflow-auto max-h-40">{content}</pre>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground text-sm">No files yet. Go to Build to create content.</p>
          )}
          
          <Button onClick={() => navigate("/build")} className="bg-primary">
            <Hammer className="w-4 h-4 mr-2" /> Open in Build
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="font-secondary text-2xl font-bold mb-6 flex items-center gap-2">
        <FolderOpen className="w-6 h-6 text-primary" /> My Projects
      </h1>
      
      <div className="flex gap-2 mb-6">
        <Input value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="New project name..." className="bg-white/5 border-white/10" />
        <Button onClick={createProject} className="bg-primary"><Plus className="w-4 h-4 mr-2" /> Create</Button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {projects.map(project => (
          <div 
            key={project.id} 
            onClick={() => openProject(project)}
            className="glass rounded-xl p-4 hover:border-primary/50 border border-white/10 cursor-pointer transition-all hover:scale-[1.02]"
          >
            <h3 className="font-semibold">{project.name}</h3>
            <p className="text-sm text-muted-foreground mt-1">{project.description || "No description"}</p>
            <p className="text-xs text-muted-foreground mt-2">Created: {new Date(project.created_at).toLocaleDateString()}</p>
          </div>
        ))}
        {projects.length === 0 && (
          <p className="text-muted-foreground col-span-2 text-center py-8">No projects yet. Create your first one!</p>
        )}
      </div>
    </div>
  );
};

// GAAIUS AI Document Studio - AI-First Document Creation & Editing Platform
const DocumentStudio = ({ onBack }) => {
  const [prompt, setPrompt] = useState("");
  const [documentContent, setDocumentContent] = useState("");
  const [documentType, setDocumentType] = useState("invoice");
  const [documentName, setDocumentName] = useState("");
  const [loading, setLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [activeTab, setActiveTab] = useState("create");
  const [generatedFiles, setGeneratedFiles] = useState([]);
  const [invoiceType, setInvoiceType] = useState("standard");
  const [downloadFormat, setDownloadFormat] = useState("pdf");
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const { user } = useAuthStore();

  // Auto-generate document name from first prompt
  const generateDocumentName = (promptText) => {
    const words = promptText.toLowerCase().split(' ');
    // Find key words to create a meaningful name
    const keyWords = ['invoice', 'quote', 'receipt', 'contract', 'proposal', 'report', 'letter', 'resume', 'nda'];
    const clientMatch = promptText.match(/(?:client|for|to)[:\s]+([A-Z][a-zA-Z\s]+?)(?:,|\.|\s+(?:project|amount|services|total))/i);
    const amountMatch = promptText.match(/\$[\d,]+(?:\.\d{2})?/);
    
    let name = "";
    
    // Find document type word
    const typeWord = keyWords.find(kw => words.includes(kw)) || documentType;
    name = typeWord.charAt(0).toUpperCase() + typeWord.slice(1);
    
    // Add client name if found
    if (clientMatch && clientMatch[1]) {
      name += ` - ${clientMatch[1].trim()}`;
    }
    
    // Add amount if found
    if (amountMatch) {
      name += ` ${amountMatch[0]}`;
    }
    
    // If name is too short, use first few meaningful words
    if (name.length < 10) {
      const meaningfulWords = words.filter(w => w.length > 3 && !['create', 'make', 'generate', 'professional', 'please', 'with', 'that', 'this', 'from'].includes(w));
      name = meaningfulWords.slice(0, 3).map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
    }
    
    return name || `${documentType.charAt(0).toUpperCase() + documentType.slice(1)} ${new Date().toLocaleDateString()}`;
  };

  const documentTypes = [
    { id: "invoice", label: "Invoice", icon: "🧾", description: "Professional invoices" },
    { id: "contract", label: "Contract/Agreement", icon: "⚖️", description: "Legal contracts" },
    { id: "proposal", label: "Business Proposal", icon: "💼", description: "Project proposals" },
    { id: "resume", label: "CV/Resume", icon: "👤", description: "Professional resumes" },
    { id: "letter", label: "Business Letter", icon: "✉️", description: "Formal letters" },
    { id: "report", label: "Report", icon: "📋", description: "Business reports" },
    { id: "pdf", label: "PDF Document", icon: "📄", description: "General PDF" },
    { id: "docx", label: "Word Document", icon: "📝", description: "MS Word format" },
    { id: "xlsx", label: "Excel Spreadsheet", icon: "📊", description: "Data spreadsheets" },
    { id: "nda", label: "NDA Agreement", icon: "🔒", description: "Non-disclosure" },
    { id: "quotation", label: "Quotation/Quote", icon: "💰", description: "Price quotes" },
    { id: "receipt", label: "Receipt", icon: "🧾", description: "Payment receipts" },
    // NEW AI-powered document types
    { id: "budget", label: "Budget Plan", icon: "💵", description: "Financial budgets" },
    { id: "inventory", label: "Inventory Sheet", icon: "📦", description: "Stock tracking" },
    { id: "timesheet", label: "Timesheet", icon: "⏰", description: "Work hours tracking" },
    { id: "expense", label: "Expense Report", icon: "💳", description: "Expense tracking" },
    { id: "payroll", label: "Payroll Sheet", icon: "💰", description: "Employee payroll" },
    { id: "project_plan", label: "Project Plan", icon: "📅", description: "Project timeline" },
    { id: "meeting_notes", label: "Meeting Minutes", icon: "📝", description: "Meeting notes" },
    { id: "sow", label: "Statement of Work", icon: "📋", description: "SOW documents" },
    { id: "purchase_order", label: "Purchase Order", icon: "🛒", description: "PO documents" },
    { id: "balance_sheet", label: "Balance Sheet", icon: "📊", description: "Financial statements" }
  ];

  const invoiceTypes = [
    { id: "standard", label: "Standard Invoice", description: "Basic invoice for products/services" },
    { id: "freelance", label: "Freelancer Invoice", description: "For independent contractors" },
    { id: "consulting", label: "Consulting Invoice", description: "Professional consulting services" },
    { id: "recurring", label: "Recurring Invoice", description: "Monthly/weekly billing" },
    { id: "proforma", label: "Proforma Invoice", description: "Preliminary bill before delivery" },
    { id: "commercial", label: "Commercial Invoice", description: "International trade/export" },
    { id: "credit", label: "Credit Note", description: "Refund or adjustment" },
    { id: "debit", label: "Debit Note", description: "Additional charges" },
    { id: "timesheet", label: "Timesheet Invoice", description: "Hourly/daily billing" },
    { id: "milestone", label: "Milestone Invoice", description: "Project milestone billing" },
    // NEW invoice types
    { id: "retainer", label: "Retainer Invoice", description: "Monthly retainer billing" },
    { id: "deposit", label: "Deposit Invoice", description: "Upfront deposit requests" },
    { id: "final", label: "Final Invoice", description: "Project completion billing" }
  ];

  const quickTemplates = {
    invoice: [
      { label: "Web Development Invoice", prompt: "Create a professional web development invoice for a React website project. Client: ABC Corp, Amount: $5,000, 50% deposit paid, balance due in 30 days. Include itemized services: Frontend development, Backend API, Database setup, Testing & QA." },
      { label: "Freelance Design Invoice", prompt: "Create a freelancer invoice for graphic design services. Client: XYZ Marketing, Services: Logo design ($500), Brand guidelines ($300), Social media templates ($200). Total: $1,000, Net 15 payment terms." },
      { label: "Consulting Services Invoice", prompt: "Create a consulting invoice for business strategy consulting. Client: StartupCo, Rate: $150/hour, Hours: 20, Total: $3,000. Include consultation sessions, market analysis, and strategic recommendations." },
      { label: "SaaS Subscription Invoice", prompt: "Create a recurring subscription invoice for SaaS software. Client: Enterprise Ltd, Plan: Professional ($299/month), Add-ons: Priority support ($50), Extra storage ($25). Total: $374/month." }
    ],
    contract: [
      { label: "Freelance Contract", prompt: "Create a freelance services contract for web development. Include scope of work, payment terms (50% upfront, 50% on completion), timeline (6 weeks), intellectual property transfer, and termination clause." },
      { label: "NDA Agreement", prompt: "Create a mutual non-disclosure agreement for business partnership discussions. Include confidentiality obligations, exclusions, term (2 years), and governing law." },
      { label: "Service Agreement", prompt: "Create a professional services agreement for ongoing marketing services. Monthly retainer: $2,500, deliverables, reporting requirements, and 30-day termination notice." }
    ],
    proposal: [
      { label: "Web Project Proposal", prompt: "Create a comprehensive web development proposal for an e-commerce website. Include executive summary, scope, timeline (12 weeks), team, technology stack (React, Node.js, PostgreSQL), pricing tiers, and terms." },
      { label: "Marketing Proposal", prompt: "Create a digital marketing proposal for a B2B company. Include current situation analysis, proposed strategy, deliverables (SEO, PPC, content marketing), KPIs, budget ($5,000/month), and ROI projections." }
    ],
    quotation: [
      { label: "Service Quotation", prompt: "Create a detailed quotation for IT support services. Include monthly support package ($1,500), on-site visits ($150/hour), hardware procurement (at cost + 10%), and software licensing management." },
      { label: "Product Quote", prompt: "Create a product quotation for office furniture supply. Items: 20 ergonomic chairs ($350 each), 20 standing desks ($500 each), 5 conference tables ($800 each). Include bulk discount 10%, delivery, and installation." }
    ],
    receipt: [
      { label: "Payment Receipt", prompt: "Create a payment receipt for consulting services. Client: Tech Solutions Inc, Amount: $2,500, Payment method: Bank Transfer, Date: Today, Reference: INV-2024-001" },
      { label: "Sales Receipt", prompt: "Create a sales receipt for software license purchase. Customer: Digital Agency, Product: Enterprise License, Amount: $999, Payment: Credit Card ending 4242" }
    ],
    // NEW AI-powered quick templates
    xlsx: [
      { label: "Budget Spreadsheet", prompt: "Create a monthly budget spreadsheet with categories: Income (Salary, Freelance, Other), Expenses (Rent, Utilities, Food, Transport, Entertainment, Savings). Include formulas for totals, remaining balance, and savings rate percentage." },
      { label: "Inventory Tracker", prompt: "Create an inventory tracking spreadsheet with columns: Item ID, Product Name, SKU, Category, Quantity, Unit Price, Total Value, Reorder Level, Supplier. Include automatic totals and low stock highlighting." },
      { label: "Sales Report", prompt: "Create a sales report spreadsheet for Q4 2024. Include monthly breakdown (Oct, Nov, Dec), product categories, units sold, revenue, cost, profit margin. Add charts for visualization." },
      { label: "Employee Timesheet", prompt: "Create a weekly employee timesheet with columns: Date, Start Time, End Time, Break, Total Hours, Overtime, Project/Task. Include weekly totals and overtime calculations." },
      { label: "Expense Tracker", prompt: "Create an expense report spreadsheet with: Date, Category (Travel, Meals, Office, Software), Description, Amount, Receipt #, Approved By. Include category summaries and monthly totals." },
      { label: "Project Tracker", prompt: "Create a project management spreadsheet with: Task Name, Assignee, Start Date, Due Date, Status (Not Started/In Progress/Complete), Priority, % Complete. Include Gantt-style timeline." }
    ],
    budget: [
      { label: "Annual Business Budget", prompt: "Create an annual business budget plan with monthly breakdowns. Categories: Revenue streams, Operating expenses (rent, utilities, salaries), Marketing, Software/Tools, Professional services, Contingency. Include YoY comparison columns." },
      { label: "Personal Finance Budget", prompt: "Create a personal monthly budget with: Income sources, Fixed expenses (mortgage, insurance, subscriptions), Variable expenses (groceries, entertainment, dining), Savings goals (emergency fund, retirement, vacation). Include pie chart data." },
      { label: "Startup Budget", prompt: "Create a 12-month startup budget with: Initial investment, Monthly burn rate, Revenue projections, Runway calculation. Categories: Product development, Marketing, Salaries, Infrastructure, Legal/Admin." }
    ],
    payroll: [
      { label: "Monthly Payroll", prompt: "Create a monthly payroll spreadsheet for 10 employees. Include: Employee ID, Name, Position, Base Salary, Overtime Hours, Overtime Pay, Deductions (Tax, Insurance, 401k), Net Pay. Add totals and company cost summary." },
      { label: "Commission Calculator", prompt: "Create a sales commission spreadsheet with: Salesperson, Total Sales, Commission Rate (tiered: 5% up to $10k, 7% $10k-$25k, 10% above $25k), Commission Earned, Bonus eligibility." }
    ],
    project_plan: [
      { label: "Software Project Plan", prompt: "Create a software development project plan with phases: Discovery (2 weeks), Design (3 weeks), Development (8 weeks), Testing (2 weeks), Deployment (1 week). Include milestones, deliverables, team allocation, and risk assessment." },
      { label: "Marketing Campaign Plan", prompt: "Create a marketing campaign project plan for product launch. Phases: Research, Content Creation, Channel Setup, Launch, Analysis. Include timeline, budget allocation, KPIs, and responsible parties." }
    ],
    sow: [
      { label: "IT Services SOW", prompt: "Create a Statement of Work for IT consulting services. Include: Project overview, Scope of work, Deliverables, Timeline, Acceptance criteria, Assumptions, Out of scope items, Payment terms ($15,000 total)." },
      { label: "Design Services SOW", prompt: "Create a Statement of Work for brand identity design. Deliverables: Logo (3 concepts), Color palette, Typography, Brand guidelines PDF, Social media templates. Timeline: 4 weeks. Revisions: 2 rounds included." }
    ],
    purchase_order: [
      { label: "Office Supplies PO", prompt: "Create a purchase order for office supplies. Vendor: Office Depot. Items: Printer paper (10 boxes @ $35), Toner cartridges (5 @ $85), Pens (50 @ $2), Notebooks (20 @ $8). Include shipping, tax, and total." },
      { label: "Equipment PO", prompt: "Create a purchase order for computer equipment. Vendor: Dell Technologies. Items: 5 laptops ($1,200 each), 5 monitors ($350 each), 5 docking stations ($200 each). Include warranty and delivery terms." }
    ],
    resume: [
      { label: "Software Developer Resume", prompt: "Create a professional software developer resume. Skills: React, Node.js, Python, AWS. Experience: 5 years. Include summary, work history (2 companies), education, certifications, and key projects." },
      { label: "Marketing Manager Resume", prompt: "Create a marketing manager resume. Skills: Digital marketing, SEO, Content strategy, Analytics. Experience: 7 years. Include achievements with metrics (increased leads 150%, reduced CAC 30%)." },
      { label: "Executive Resume", prompt: "Create a C-level executive resume for a CEO position. Include: Executive summary, Career highlights with revenue/growth metrics, Board experience, Education (MBA), Industry expertise." }
    ],
    meeting_notes: [
      { label: "Board Meeting Minutes", prompt: "Create board meeting minutes template. Include: Date, Attendees, Agenda items, Motions/Votes, Action items with owners and deadlines, Next meeting date. Format for official record keeping." },
      { label: "Project Standup Notes", prompt: "Create daily standup meeting notes template. Include: Date, Team members, Yesterday's accomplishments, Today's goals, Blockers/Issues, Follow-up items." }
    ],
    balance_sheet: [
      { label: "Company Balance Sheet", prompt: "Create a company balance sheet. Assets: Current (Cash, AR, Inventory), Fixed (Equipment, Property). Liabilities: Current (AP, Short-term debt), Long-term (Loans, Bonds). Equity: Common stock, Retained earnings. Include totals and verification (A=L+E)." },
      { label: "Personal Net Worth Statement", prompt: "Create a personal net worth statement. Assets: Cash/Savings, Investments (Stocks, Bonds, 401k), Real estate, Vehicles. Liabilities: Mortgage, Car loans, Credit cards, Student loans. Calculate net worth." }
    ]
  };

  const handleGenerate = async () => {
    if (!prompt.trim() || loading) return;
    setLoading(true);
    
    // Auto-generate document name if empty
    if (!documentName.trim()) {
      setDocumentName(generateDocumentName(prompt));
    }
    
    // Build enhanced prompt based on document type
    let enhancedPrompt = prompt;
    if (documentType === "invoice" && invoiceType !== "standard") {
      enhancedPrompt = `Create a ${invoiceTypes.find(t => t.id === invoiceType)?.label || invoiceType} invoice. ${prompt}`;
    }
    
    setChatHistory(prev => [...prev, { role: "user", content: prompt }]);
    
    try {
      const res = await api.post("/document/generate-professional", { 
        prompt: enhancedPrompt, 
        document_type: documentType,
        current_content: documentContent,
        document_name: documentName || generateDocumentName(prompt),
        output_format: downloadFormat
      });
      
      if (res.data.content) {
        setDocumentContent(res.data.content);
      }
      if (res.data.file_url) {
        const fileName = documentName || generateDocumentName(prompt);
        setGeneratedFiles(prev => [{ 
          name: res.data.filename || `${fileName}.${res.data.format || 'pdf'}`,
          url: res.data.file_url,
          type: documentType,
          format: res.data.format || 'pdf',
          timestamp: new Date().toISOString()
        }, ...prev]);
      }
      
      // Auto-set document name if not set
      if (!documentName.trim()) {
        setDocumentName(generateDocumentName(prompt));
      }
      
      setChatHistory(prev => [...prev, { 
        role: "assistant", 
        content: res.data.message || `✅ Your ${documentType} has been created! You can preview and edit it on the right, then download as PDF.`
      }]);
      toast.success("Document generated!");
    } catch (error) {
      // Fallback to regular document generation
      try {
        const fallbackRes = await api.post("/document/generate", { 
          prompt: enhancedPrompt, 
          document_type: documentType,
          document_name: documentName || generateDocumentName(prompt)
        });
        if (fallbackRes.data) {
          setDocumentContent(fallbackRes.data.content || "");
          if (fallbackRes.data.file_url) {
            setGeneratedFiles(prev => [{ 
              name: `${documentName || generateDocumentName(prompt)}.pdf`,
              url: fallbackRes.data.file_url,
              type: documentType,
              format: 'pdf',
              timestamp: new Date().toISOString()
            }, ...prev]);
          }
          if (!documentName.trim()) {
            setDocumentName(generateDocumentName(prompt));
          }
          setChatHistory(prev => [...prev, { 
            role: "assistant", 
            content: "✅ Document created! You can edit it in the preview panel."
          }]);
        }
      } catch (e) {
        setChatHistory(prev => [...prev, { role: "assistant", content: "❌ Error generating document. Please try again." }]);
        toast.error("Generation failed");
      }
    } finally {
      setLoading(false);
      setPrompt("");
    }
  };

  const downloadDocument = async (format = "pdf") => {
    if (!documentContent && generatedFiles.length === 0) {
      toast.error("No document to download");
      return;
    }
    
    // If we have a generated file URL, use it
    if (generatedFiles.length > 0 && generatedFiles[0].url) {
      window.open(`${BACKEND_URL}${generatedFiles[0].url}`, '_blank');
      toast.success("Download started!");
      return;
    }
    
    // Otherwise, generate and download
    try {
      const res = await api.post("/document/download", {
        content: documentContent,
        document_type: documentType,
        document_name: documentName || "Document",
        format: format
      }, { responseType: 'blob' });
      
      const blob = new Blob([res.data], { 
        type: format === 'pdf' ? 'application/pdf' : 
              format === 'xlsx' ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' :
              format === 'docx' ? 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' :
              'text/plain'
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${documentName || 'Document'}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success(`Downloaded as ${format.toUpperCase()}!`);
    } catch (error) {
      // Fallback to text download
      const blob = new Blob([documentContent], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${documentName || 'Document'}.txt`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Downloaded!");
    }
    setShowDownloadMenu(false);
  };

  const applyTemplate = (template) => {
    setPrompt(template.prompt);
    toast.info(`Template loaded: ${template.label}`);
  };

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-[#0a0a0a] via-[#0f0f1a] to-[#0a0a0a]">
      {/* Header */}
      <div className="h-14 border-b border-white/10 flex items-center justify-between px-4 bg-[#0d0d0d]/80 backdrop-blur-xl">
        <div className="flex items-center gap-4">
          <Button size="sm" variant="ghost" onClick={onBack} className="h-8">
            <X className="w-4 h-4 mr-1" /> Back
          </Button>
          <div className="h-6 w-px bg-white/20" />
          <h2 className="font-secondary text-base font-bold flex items-center gap-2">
            <FileCode className="w-5 h-5 text-cyan-400" /> GAAIUS AI Document Studio
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <Input 
            value={documentName} 
            onChange={(e) => setDocumentName(e.target.value)}
            className="w-56 h-8 text-sm bg-white/5 border-white/10"
            placeholder="Auto-named from your request..."
          />
        </div>
      </div>
      
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Document Types & Templates */}
        <div className="w-72 border-r border-white/10 flex flex-col bg-[#0d0d0d]">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
            <TabsList className="w-full grid grid-cols-3 m-2 bg-white/5">
              <TabsTrigger value="create" className="text-xs">Types</TabsTrigger>
              <TabsTrigger value="templates" className="text-xs">Templates</TabsTrigger>
              <TabsTrigger value="history" className="text-xs">Files</TabsTrigger>
            </TabsList>
            
            <TabsContent value="create" className="flex-1 p-3 space-y-2 overflow-auto">
              <p className="text-xs text-muted-foreground uppercase font-mono mb-2">Document Type</p>
              <ScrollArea className="h-[calc(100vh-200px)]">
                {documentTypes.map(dt => (
                  <button
                    key={dt.id}
                    onClick={() => setDocumentType(dt.id)}
                    className={`w-full flex items-center gap-2 p-2.5 rounded-lg text-sm transition mb-1 ${documentType === dt.id ? "bg-cyan-500/20 border border-cyan-500/40" : "hover:bg-white/5"}`}
                  >
                    <span className="text-lg">{dt.icon}</span>
                    <div className="text-left">
                      <span className="block">{dt.label}</span>
                      <span className="text-xs text-muted-foreground">{dt.description}</span>
                    </div>
                  </button>
                ))}
              </ScrollArea>
              
              {documentType === "invoice" && (
                <div className="mt-4 pt-4 border-t border-white/10">
                  <p className="text-xs text-muted-foreground uppercase font-mono mb-2">Invoice Type</p>
                  <Select value={invoiceType} onValueChange={setInvoiceType}>
                    <SelectTrigger className="w-full bg-white/5 border-white/10 text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {invoiceTypes.map(it => (
                        <SelectItem key={it.id} value={it.id}>
                          <div>
                            <span>{it.label}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground mt-2">
                    {invoiceTypes.find(t => t.id === invoiceType)?.description}
                  </p>
                </div>
              )}
            </TabsContent>
            
            <TabsContent value="templates" className="flex-1 p-3 overflow-auto">
              <p className="text-xs text-muted-foreground uppercase font-mono mb-2">Quick Templates</p>
              <ScrollArea className="h-[calc(100vh-200px)]">
                {(quickTemplates[documentType] || quickTemplates.invoice).map((template, i) => (
                  <button
                    key={i}
                    onClick={() => applyTemplate(template)}
                    className="w-full text-left p-3 rounded-lg hover:bg-white/5 border border-white/5 mb-2 transition"
                  >
                    <p className="text-sm font-medium text-cyan-400">{template.label}</p>
                    <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{template.prompt.slice(0, 80)}...</p>
                  </button>
                ))}
              </ScrollArea>
            </TabsContent>
            
            <TabsContent value="history" className="flex-1 p-3 overflow-auto">
              <p className="text-xs text-muted-foreground uppercase font-mono mb-2">Generated Files</p>
              {generatedFiles.length === 0 ? (
                <p className="text-xs text-muted-foreground text-center py-4">No files yet</p>
              ) : (
                <div className="space-y-2">
                  {generatedFiles.map((file, i) => (
                    <div key={i} className="glass-light rounded-lg p-3 text-xs">
                      <p className="font-medium truncate">{file.name}</p>
                      <p className="text-muted-foreground">{new Date(file.timestamp).toLocaleTimeString()}</p>
                      <Button size="sm" variant="ghost" onClick={() => downloadDocument(file)} className="w-full mt-2 h-7 text-xs bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400">
                        <Download className="w-3 h-3 mr-1" /> Download
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
        
        {/* Middle - AI Chat */}
        <div className="w-96 border-r border-white/10 flex flex-col bg-[#0a0a0a]">
          <div className="p-4 border-b border-white/10">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-cyan-400" />
              <span className="font-semibold">AI Document Assistant</span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Creating: <span className="text-cyan-400">{documentTypes.find(d => d.id === documentType)?.label}</span>
              {documentType === "invoice" && <span className="text-muted-foreground"> ({invoiceTypes.find(t => t.id === invoiceType)?.label})</span>}
            </p>
          </div>
          
          <ScrollArea className="flex-1 p-4">
            {chatHistory.length === 0 ? (
              <div className="text-center py-6">
                <div className="w-16 h-16 rounded-2xl bg-cyan-500/20 flex items-center justify-center mx-auto mb-4">
                  <FileCode className="w-8 h-8 text-cyan-400" />
                </div>
                <p className="text-sm text-muted-foreground mb-4">Describe your {documentTypes.find(d => d.id === documentType)?.label.toLowerCase()}</p>
                <div className="space-y-2 text-xs text-left">
                  {documentType === "invoice" ? (
                    <>
                      <p className="text-cyan-400/80 cursor-pointer hover:text-cyan-400 p-2 rounded hover:bg-white/5" onClick={() => setPrompt("Create a professional invoice for web development services. Client: ABC Company, Project: Website Redesign, Amount: $5,000, Payment terms: Net 30")}>
                        💡 Web development invoice - $5,000
                      </p>
                      <p className="text-cyan-400/80 cursor-pointer hover:text-cyan-400 p-2 rounded hover:bg-white/5" onClick={() => setPrompt("Create a freelance design invoice. Client: XYZ Marketing, Services: Logo design, Brand guidelines, Social media kit. Total: $1,200, Due in 15 days")}>
                        💡 Freelance design invoice - $1,200
                      </p>
                      <p className="text-cyan-400/80 cursor-pointer hover:text-cyan-400 p-2 rounded hover:bg-white/5" onClick={() => setPrompt("Create a consulting services invoice with hourly rate. Client: StartupCo, Rate: $150/hr, Hours: 25, Total: $3,750. Include strategy sessions and market analysis")}>
                        💡 Consulting hourly invoice - $3,750
                      </p>
                      <p className="text-cyan-400/80 cursor-pointer hover:text-cyan-400 p-2 rounded hover:bg-white/5" onClick={() => setPrompt("Create a recurring monthly SaaS subscription invoice. Client: Enterprise Ltd, Plan: Professional ($299), Addons: Priority support ($50), Storage ($25), Total: $374/month")}>
                        💡 SaaS subscription invoice - $374/mo
                      </p>
                    </>
                  ) : (
                    <>
                      {/* Show quickTemplates if available for this document type */}
                      {quickTemplates[documentType] ? (
                        quickTemplates[documentType].slice(0, 4).map((template, idx) => (
                          <p key={idx} className="text-cyan-400/80 cursor-pointer hover:text-cyan-400 p-2 rounded hover:bg-white/5" onClick={() => setPrompt(template.prompt)}>
                            💡 {template.label}
                          </p>
                        ))
                      ) : (
                        <>
                          <p className="text-cyan-400/80 cursor-pointer hover:text-cyan-400 p-2 rounded hover:bg-white/5" onClick={() => setPrompt(`Create a professional ${documentTypes.find(d => d.id === documentType)?.label.toLowerCase()} for a technology company`)}>
                            💡 "{documentTypes.find(d => d.id === documentType)?.label} for tech company"
                          </p>
                          <p className="text-cyan-400/80 cursor-pointer hover:text-cyan-400 p-2 rounded hover:bg-white/5" onClick={() => setPrompt(`Create a detailed ${documentTypes.find(d => d.id === documentType)?.label.toLowerCase()} with professional formatting`)}>
                            💡 "Detailed professional {documentTypes.find(d => d.id === documentType)?.label.toLowerCase()}"
                          </p>
                        </>
                      )}
                    </>
                  )}
                </div>
              </div>
            ) : (
              <div className="space-y-5" style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif' }}>
                {chatHistory.map((msg, i) => (
                  <div key={i} className={`rounded-xl text-sm ${msg.role === "user" ? "bg-cyan-500/10 border border-cyan-500/20 p-4 ml-6" : "bg-transparent"}`} style={{ marginBottom: '20px' }}>
                    <div className="flex items-center gap-2 mb-3">
                      <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold ${msg.role === "user" ? "bg-cyan-500" : "bg-gradient-to-br from-violet-500 to-cyan-500"}`}>
                        {msg.role === "user" ? "U" : "G"}
                      </div>
                      <span className="text-sm font-medium text-white/80">{msg.role === "user" ? "You" : "GAAIUS AI"}</span>
                    </div>
                    <div className="pl-9" style={{ lineHeight: '1.6' }}>
                      {msg.content.split('\n\n').map((paragraph, pIdx) => (
                        <div key={pIdx} style={{ marginBottom: '16px' }}>
                          {paragraph.split('\n').map((line, lIdx) => {
                            const isBullet = line.startsWith('•') || line.startsWith('-') || line.startsWith('*') || line.match(/^\d+\./);
                            return (
                              <p key={lIdx} style={{ 
                                marginBottom: isBullet ? '8px' : '4px', 
                                paddingLeft: isBullet ? '20px' : '0',
                                lineHeight: '1.6'
                              }}>
                                {line}
                              </p>
                            );
                          })}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
          
          <div className="p-4 border-t border-white/10">
            <div className="flex gap-2">
              <Input
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder={`Describe your ${documentType}...`}
                className="flex-1 bg-white/5 border-white/10 h-11 text-sm px-4"
                style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}
                onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
              />
              <Button onClick={handleGenerate} disabled={loading} className="bg-cyan-600 hover:bg-cyan-700 h-11 px-5">
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </Button>
            </div>
          </div>
        </div>
        
        {/* Right - Document Preview */}
        <div className="flex-1 flex flex-col bg-[#111]">
          <div className="h-10 border-b border-white/10 flex items-center justify-between px-4">
            <div className="flex items-center gap-2">
              <Eye className="w-4 h-4 text-cyan-400" />
              <span className="text-sm font-mono">Document Preview</span>
              {documentContent && (
                <Button 
                  size="sm" 
                  variant="ghost" 
                  onClick={() => setIsEditing(!isEditing)} 
                  className={`h-6 text-xs ml-2 ${isEditing ? 'bg-cyan-500/20 text-cyan-400' : ''}`}
                >
                  <Edit className="w-3 h-3 mr-1" /> {isEditing ? "Preview" : "Edit"}
                </Button>
              )}
            </div>
            {documentContent && (
              <div className="flex items-center gap-2 relative">
                <Button 
                  size="sm" 
                  onClick={() => setShowDownloadMenu(!showDownloadMenu)}
                  className="h-7 text-xs bg-cyan-600 hover:bg-cyan-700"
                >
                  <Download className="w-3 h-3 mr-1" /> DOWNLOAD
                </Button>
                {showDownloadMenu && (
                  <div className="absolute top-full right-0 mt-1 bg-[#1a1a1a] border border-white/10 rounded-lg shadow-xl z-50 min-w-[150px]">
                    <button onClick={() => downloadDocument("pdf")} className="w-full px-3 py-2 text-left text-xs hover:bg-white/5 flex items-center gap-2">
                      📄 PDF (Default)
                    </button>
                    <button onClick={() => downloadDocument("docx")} className="w-full px-3 py-2 text-left text-xs hover:bg-white/5 flex items-center gap-2">
                      📝 Word (.docx)
                    </button>
                    {(documentType === "xlsx" || documentContent.includes(',')) && (
                      <button onClick={() => downloadDocument("xlsx")} className="w-full px-3 py-2 text-left text-xs hover:bg-white/5 flex items-center gap-2">
                        📊 Excel (.xlsx)
                      </button>
                    )}
                    <button onClick={() => downloadDocument("txt")} className="w-full px-3 py-2 text-left text-xs hover:bg-white/5 flex items-center gap-2">
                      📃 Text (.txt)
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
          <div className="flex-1 overflow-auto bg-white">
            {documentContent ? (
              isEditing ? (
                <textarea
                  value={documentContent}
                  onChange={(e) => setDocumentContent(e.target.value)}
                  className="w-full h-full p-6 text-black text-sm font-mono resize-none focus:outline-none"
                  placeholder="Edit your document here..."
                />
              ) : (
                <div className="max-w-3xl mx-auto p-8 text-black">
                  {/* Render MODERN formatted document preview */}
                  {(() => {
                    try {
                      const data = JSON.parse(documentContent);
                      
                      if (documentType === "invoice") {
                        return (
                          <div className="bg-white shadow-lg rounded-lg overflow-hidden">
                            {/* Header */}
                            <div className="flex justify-between items-start p-8 border-b">
                              <div>
                                <h1 className="text-3xl font-bold text-gray-800">{data.company?.name || "Your Company"}</h1>
                                <p className="text-gray-500 text-sm mt-1">{data.company?.address}</p>
                                <p className="text-gray-500 text-sm">{data.company?.city}</p>
                                <p className="text-gray-500 text-sm">{data.company?.email} | {data.company?.phone}</p>
                              </div>
                              <div className="text-right">
                                <h2 className="text-4xl font-bold text-green-600">INVOICE</h2>
                                <p className="text-gray-600 mt-2">#{data.invoice_number}</p>
                              </div>
                            </div>
                            
                            {/* Info Bar */}
                            <div className="grid grid-cols-4 bg-green-600 text-white text-sm">
                              <div className="p-4 border-r border-green-500">
                                <p className="opacity-80">Invoice No.</p>
                                <p className="font-semibold">{data.invoice_number}</p>
                              </div>
                              <div className="p-4 border-r border-green-500">
                                <p className="opacity-80">Issue Date</p>
                                <p className="font-semibold">{data.date}</p>
                              </div>
                              <div className="p-4 border-r border-green-500">
                                <p className="opacity-80">Due Date</p>
                                <p className="font-semibold">{data.due_date}</p>
                              </div>
                              <div className="p-4 bg-gray-800">
                                <p className="opacity-80">Total Due</p>
                                <p className="font-bold text-lg">${(data.total || 0).toLocaleString('en-US', {minimumFractionDigits: 2})}</p>
                              </div>
                            </div>
                            
                            {/* Bill To */}
                            <div className="p-8">
                              <p className="text-gray-500 text-sm uppercase tracking-wide mb-2">Bill To</p>
                              <p className="font-semibold text-lg">{data.client?.name}</p>
                              <p className="text-gray-600">{data.client?.address}</p>
                              <p className="text-gray-600">{data.client?.city}</p>
                              {data.client?.email && <p className="text-gray-600">{data.client?.email}</p>}
                            </div>
                            
                            {/* Items Table */}
                            <div className="px-8">
                              <table className="w-full">
                                <thead>
                                  <tr className="bg-green-600 text-white text-sm">
                                    <th className="text-left p-3">DESCRIPTION</th>
                                    <th className="text-center p-3 w-20">QTY</th>
                                    <th className="text-right p-3 w-28">RATE</th>
                                    <th className="text-right p-3 w-28">AMOUNT</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {(data.items || []).map((item, i) => (
                                    <tr key={i} className={i % 2 === 0 ? "bg-gray-50" : "bg-white"}>
                                      <td className="p-3 border-b">{item.description}</td>
                                      <td className="p-3 border-b text-center">{item.quantity}</td>
                                      <td className="p-3 border-b text-right">${(item.rate || item.unit_price || 0).toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                                      <td className="p-3 border-b text-right">${(item.amount || item.total || 0).toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                            
                            {/* Totals */}
                            <div className="p-8 flex justify-end">
                              <div className="w-64">
                                <div className="flex justify-between py-2">
                                  <span className="text-gray-600">Subtotal:</span>
                                  <span>${(data.subtotal || 0).toLocaleString('en-US', {minimumFractionDigits: 2})}</span>
                                </div>
                                <div className="flex justify-between py-2">
                                  <span className="text-gray-600">Tax ({data.tax_rate || 0}%):</span>
                                  <span>${(data.tax || 0).toLocaleString('en-US', {minimumFractionDigits: 2})}</span>
                                </div>
                                <div className="flex justify-between py-3 border-t-2 border-green-600 mt-2">
                                  <span className="font-bold text-lg text-green-600">TOTAL:</span>
                                  <span className="font-bold text-lg text-green-600">${(data.total || 0).toLocaleString('en-US', {minimumFractionDigits: 2})}</span>
                                </div>
                              </div>
                            </div>
                            
                            {/* Footer */}
                            {(data.notes || data.payment_info) && (
                              <div className="px-8 pb-8 text-sm text-gray-600">
                                {data.notes && <p><strong>Notes:</strong> {data.notes}</p>}
                                {data.payment_info && <p className="mt-2"><strong>Payment Info:</strong> {data.payment_info}</p>}
                              </div>
                            )}
                            
                            <div className="bg-gray-50 p-4 text-center text-gray-500 text-sm">
                              Thank you for your business!
                            </div>
                          </div>
                        );
                      }
                      
                      if (documentType === "quotation") {
                        return (
                          <div className="bg-white shadow-lg rounded-lg overflow-hidden">
                            <div className="flex justify-between items-start p-8 border-b">
                              <div>
                                <h1 className="text-3xl font-bold text-gray-800">{data.company?.name || "Your Company"}</h1>
                                <p className="text-gray-500 text-sm mt-1">{data.company?.address}</p>
                                <p className="text-gray-500 text-sm">{data.company?.city}</p>
                              </div>
                              <div className="text-right">
                                <h2 className="text-4xl font-bold text-green-600">QUOTE</h2>
                                <p className="text-gray-600 mt-2">#{data.quote_number}</p>
                              </div>
                            </div>
                            
                            <div className="grid grid-cols-4 bg-green-600 text-white text-sm">
                              <div className="p-4 border-r border-green-500">
                                <p className="opacity-80">Quote No.</p>
                                <p className="font-semibold">{data.quote_number}</p>
                              </div>
                              <div className="p-4 border-r border-green-500">
                                <p className="opacity-80">Date</p>
                                <p className="font-semibold">{data.date}</p>
                              </div>
                              <div className="p-4 border-r border-green-500">
                                <p className="opacity-80">Valid Until</p>
                                <p className="font-semibold">{data.valid_until}</p>
                              </div>
                              <div className="p-4 bg-gray-800">
                                <p className="opacity-80">Total</p>
                                <p className="font-bold text-lg">${(data.total || 0).toLocaleString('en-US', {minimumFractionDigits: 2})}</p>
                              </div>
                            </div>
                            
                            <div className="p-8">
                              <p className="text-gray-500 text-sm uppercase tracking-wide mb-2">Quote For</p>
                              <p className="font-semibold text-lg">{data.client?.name}</p>
                              {data.client?.company && <p className="text-gray-600">{data.client?.company}</p>}
                              <p className="text-gray-600">{data.client?.address}</p>
                            </div>
                            
                            <div className="px-8">
                              <table className="w-full">
                                <thead>
                                  <tr className="bg-green-600 text-white text-sm">
                                    <th className="text-left p-3">DESCRIPTION</th>
                                    <th className="text-center p-3 w-20">QTY</th>
                                    <th className="text-right p-3 w-28">UNIT PRICE</th>
                                    <th className="text-right p-3 w-28">TOTAL</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {(data.items || []).map((item, i) => (
                                    <tr key={i} className={i % 2 === 0 ? "bg-gray-50" : "bg-white"}>
                                      <td className="p-3 border-b">{item.description}</td>
                                      <td className="p-3 border-b text-center">{item.quantity}</td>
                                      <td className="p-3 border-b text-right">${(item.unit_price || 0).toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                                      <td className="p-3 border-b text-right">${(item.total || 0).toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                            
                            <div className="p-8 flex justify-end">
                              <div className="w-64">
                                <div className="flex justify-between py-2">
                                  <span className="text-gray-600">Subtotal:</span>
                                  <span>${(data.subtotal || 0).toLocaleString('en-US', {minimumFractionDigits: 2})}</span>
                                </div>
                                {data.discount > 0 && (
                                  <div className="flex justify-between py-2 text-red-500">
                                    <span>Discount:</span>
                                    <span>-${(data.discount || 0).toLocaleString('en-US', {minimumFractionDigits: 2})}</span>
                                  </div>
                                )}
                                <div className="flex justify-between py-3 border-t-2 border-green-600 mt-2">
                                  <span className="font-bold text-lg text-green-600">TOTAL:</span>
                                  <span className="font-bold text-lg text-green-600">${(data.total || 0).toLocaleString('en-US', {minimumFractionDigits: 2})}</span>
                                </div>
                              </div>
                            </div>
                            
                            {data.terms && (
                              <div className="px-8 pb-8 text-sm text-gray-600">
                                <p><strong>Terms & Conditions:</strong> {data.terms}</p>
                              </div>
                            )}
                          </div>
                        );
                      }
                      
                      if (documentType === "receipt") {
                        return (
                          <div className="bg-white shadow-lg rounded-lg overflow-hidden max-w-md mx-auto">
                            <div className="text-center p-6 border-b">
                              <h2 className="text-3xl font-bold text-gray-800">RECEIPT</h2>
                              <h3 className="text-xl font-semibold mt-2">{data.company?.name || "Shop Name"}</h3>
                              <p className="text-gray-500 text-sm">{data.company?.address}</p>
                              <p className="text-gray-500 text-sm">{data.company?.city}</p>
                              <p className="text-gray-500 text-sm">{data.company?.phone}</p>
                            </div>
                            
                            <div className="p-4 text-center border-b border-dashed">
                              <p className="font-semibold">Receipt #{data.receipt_number}</p>
                              <p className="text-gray-500 text-sm">{data.date}</p>
                            </div>
                            
                            {data.customer?.name && (
                              <div className="px-6 py-3 border-b">
                                <p className="text-sm text-gray-600">Customer: {data.customer?.name}</p>
                              </div>
                            )}
                            
                            <div className="p-6">
                              <table className="w-full text-sm">
                                <thead>
                                  <tr className="border-b-2 border-gray-300">
                                    <th className="text-left py-2">Item</th>
                                    <th className="text-center py-2">Qty</th>
                                    <th className="text-right py-2">Price</th>
                                    <th className="text-right py-2">Total</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {(data.items || []).map((item, i) => (
                                    <tr key={i} className="border-b border-gray-200">
                                      <td className="py-2">{item.description}</td>
                                      <td className="py-2 text-center">{item.quantity}</td>
                                      <td className="py-2 text-right">${(item.price || 0).toFixed(2)}</td>
                                      <td className="py-2 text-right">${(item.total || 0).toFixed(2)}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                            
                            <div className="px-6 pb-4 border-t border-dashed">
                              <div className="flex justify-between py-2">
                                <span>Subtotal:</span>
                                <span>${(data.subtotal || 0).toFixed(2)}</span>
                              </div>
                              <div className="flex justify-between py-2">
                                <span>Tax:</span>
                                <span>${(data.tax || 0).toFixed(2)}</span>
                              </div>
                              <div className="flex justify-between py-3 border-t-2 border-black font-bold text-lg">
                                <span>TOTAL:</span>
                                <span>${(data.total || 0).toFixed(2)}</span>
                              </div>
                            </div>
                            
                            <div className="px-6 pb-4 text-center text-sm border-t border-dashed">
                              <p className="py-2">Payment: {data.payment_method}</p>
                              {data.payment_reference && <p className="text-gray-500">Ref: {data.payment_reference}</p>}
                            </div>
                            
                            <div className="bg-gray-50 p-4 text-center text-gray-600">
                              {data.notes || "Thank you for your purchase!"}
                            </div>
                          </div>
                        );
                      }
                      
                      // For Excel - show as table
                      if (documentType === "xlsx") {
                        const rows = documentContent.split('\n').filter(r => r.trim());
                        return (
                          <div className="bg-white shadow-lg rounded-lg overflow-hidden">
                            <div className="p-4 bg-green-600 text-white font-semibold">
                              Excel Spreadsheet Preview
                            </div>
                            <div className="overflow-x-auto">
                              <table className="w-full text-sm">
                                {rows.map((row, i) => {
                                  const cells = row.split(',');
                                  return (
                                    <tr key={i} className={i === 0 ? "bg-gray-100 font-semibold" : (i % 2 === 0 ? "bg-gray-50" : "")}>
                                      {cells.map((cell, j) => (
                                        <td key={j} className="border px-3 py-2">{cell.trim()}</td>
                                      ))}
                                    </tr>
                                  );
                                })}
                              </table>
                            </div>
                          </div>
                        );
                      }
                      
                      // Fallback - show as text
                      throw new Error("Not JSON");
                    } catch (e) {
                      // Not JSON, show as formatted text
                      return (
                        <div className="prose prose-sm max-w-none">
                          <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-gray-800 p-6 bg-gray-50 rounded-lg">{documentContent}</pre>
                        </div>
                      );
                    }
                  })()}
                </div>
              )
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-gray-400">
                <FileCode className="w-16 h-16 mb-4 opacity-30" />
                <p className="text-lg">Your document will appear here</p>
                <p className="text-sm">Tell the AI what to create using the chat</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Social Media Builder Component - TikTok + Facebook + Instagram Clone
const SocialMediaBuilder = ({ navigate, user, showAuth, showProfile, logout }) => {
  const [activeTab, setActiveTab] = useState("feed"); // feed | create | messages | notifications | analytics | profile
  const [socialPosts, setSocialPosts] = useState([]);
  const [userProfile, setUserProfile] = useState(null);
  const [draftContent, setDraftContent] = useState("");
  const [selectedMedia, setSelectedMedia] = useState(null);
  const [mediaType, setMediaType] = useState("photo"); // photo | video | reel | story
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingFeed, setLoadingFeed] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [messages, setMessages] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messageText, setMessageText] = useState("");
  const [analytics, setAnalytics] = useState(null);
  const [aiEnhance, setAiEnhance] = useState(true);
  const fileInputRef = useRef(null);

  const SOCIAL_FEATURES = [
    { id: "feed", label: "Feed", icon: MessageSquare, desc: "Browse trending posts & stories" },
    { id: "create", label: "Create", icon: Plus, desc: "Post photos, videos, reels & stories" },
    { id: "duet-collab", label: "Duet & Collab", icon: Users, desc: "Record videos together with collaborators" },
    { id: "messages", label: "Messages", icon: MessageSquare, desc: "Chat with friends & followers" },
    { id: "notifications", label: "Notifications", icon: Sparkles, desc: "Likes, comments & follows" },
    { id: "analytics", label: "Analytics", icon: Zap, desc: "Track engagement & reach" },
    { id: "profile", label: "Profile", icon: User, desc: "Manage your profile" }
  ];

  // Load feed when switching to feed tab
  useEffect(() => {
    if (activeTab === "feed" && user) {
      loadFeed();
    }
  }, [activeTab, user]);

  // Load profile when switching to profile tab
  useEffect(() => {
    if (activeTab === "profile" && user) {
      loadProfile();
    }
  }, [activeTab, user]);

  // Load notifications when switching to notifications tab
  useEffect(() => {
    if (activeTab === "notifications" && user) {
      loadNotifications();
    }
  }, [activeTab, user]);

  // Load analytics when switching to analytics tab
  useEffect(() => {
    if (activeTab === "analytics" && user) {
      loadAnalytics();
    }
  }, [activeTab, user]);

  // Load profile on component mount
  useEffect(() => {
    if (user) {
      loadProfile();
    }
  }, [user]);

  const loadProfile = async () => {
    try {
      const response = await api.get(`/social/profile/${user.id}`);
      setUserProfile(response.data);
    } catch (error) {
      console.error("Error loading profile:", error);
    }
  };

  const loadFeed = async () => {
    setLoadingFeed(true);
    try {
      const response = await api.get("/social/feed", { params: { skip: 0, limit: 20 } });
      setSocialPosts(response.data.posts || []);
    } catch (error) {
      console.error("Error loading feed:", error);
      toast.error("Failed to load feed");
    } finally {
      setLoadingFeed(false);
    }
  };

  const loadNotifications = async () => {
    try {
      const response = await api.get("/social/notifications", { params: { skip: 0, limit: 20 } });
      setNotifications(response.data.notifications || []);
    } catch (error) {
      console.error("Error loading notifications:", error);
    }
  };

  const loadAnalytics = async () => {
    try {
      const response = await api.get("/social/analytics");
      setAnalytics(response.data);
    } catch (error) {
      console.error("Error loading analytics:", error);
    }
  };

  const handleMediaSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Determine media type from file
    const fileType = file.type;
    let detectedType = "photo";
    if (fileType.includes("video")) detectedType = "video";
    else if (fileType.includes("image")) detectedType = "photo";
    setMediaType(detectedType);

    // For now, store as local preview
    const reader = new FileReader();
    reader.onload = (event) => {
      setSelectedMedia({
        file,
        preview: event.target.result,
        type: detectedType
      });
    };
    reader.readAsDataURL(file);
  };

  const uploadMedia = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("media_type", mediaType);

    try {
      const response = await api.post("/social/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      return response.data;
    } catch (error) {
      console.error("Error uploading media:", error);
      throw error;
    }
  };

  const createPost = async () => {
    if (!user) {
      showAuth();
      return;
    }

    if (!draftContent.trim() && !selectedMedia) {
      toast.error("Add content or media to create a post");
      return;
    }

    setLoading(true);
    try {
      let mediaItems = [];

      // Upload media if selected
      if (selectedMedia && selectedMedia.file) {
        try {
          const uploadedMedia = await uploadMedia(selectedMedia.file);
          mediaItems = [uploadedMedia];
        } catch (error) {
          toast.error("Failed to upload media");
          setLoading(false);
          return;
        }
      }

      // Create post via API
      const response = await api.post("/social/posts", {
        content: draftContent,
        media_items: mediaItems,
        ai_enhance: aiEnhance
      });

      setSocialPosts(prev => [response.data, ...prev]);
      setDraftContent("");
      setSelectedMedia(null);
      setShowCreateModal(false);
      toast.success("Post created successfully! 🎉");
    } catch (error) {
      console.error("Error creating post:", error);
      toast.error("Failed to create post");
    } finally {
      setLoading(false);
    }
  };

  const likePost = async (postId) => {
    try {
      await api.post(`/social/posts/${postId}/like`);
      setSocialPosts(prev =>
        prev.map(post =>
          post._id === postId
            ? { ...post, likes_count: (post.likes_count || 0) + 1, user_liked: true }
            : post
        )
      );
    } catch (error) {
      console.error("Error liking post:", error);
    }
  };

  const unlikePost = async (postId) => {
    try {
      await api.delete(`/social/posts/${postId}/like`);
      setSocialPosts(prev =>
        prev.map(post =>
          post._id === postId
            ? { ...post, likes_count: Math.max(0, (post.likes_count || 1) - 1), user_liked: false }
            : post
        )
      );
    } catch (error) {
      console.error("Error unliking post:", error);
    }
  };

  const repostPost = async (postId) => {
    try {
      await api.post(`/social/posts/${postId}/repost`);
      toast.success("Post reposted!");
    } catch (error) {
      console.error("Error reposting:", error);
      toast.error("Failed to repost");
    }
  };

  const sharePost = async (postId) => {
    try {
      await api.post(`/social/posts/${postId}/share`);
      toast.success("Post shared!");
    } catch (error) {
      console.error("Error sharing post:", error);
      toast.error("Failed to share post");
    }
  };

  const followUser = async (userId) => {
    try {
      await api.post(`/social/users/${userId}/follow`);
      toast.success("Following!");
    } catch (error) {
      console.error("Error following:", error);
      toast.error("Failed to follow");
    }
  };

  const sendMessage = async (recipientId, content) => {
    if (!content.trim()) return;

    try {
      const response = await api.post("/social/messages", {
        recipient_id: recipientId,
        content
      });
      setMessages(prev => [...prev, response.data]);
      setMessageText("");
    } catch (error) {
      console.error("Error sending message:", error);
      toast.error("Failed to send message");
    }
  };

  const getTrendingPosts = async () => {
    try {
      const response = await api.get("/social/trending", { params: { skip: 0, limit: 10 } });
      return response.data.posts || [];
    } catch (error) {
      console.error("Error loading trending:", error);
      return [];
    }
  };

  return (
    <div className="h-screen w-full bg-[#050505] text-white overflow-hidden flex">
      {/* Left Sidebar - Navigation */}
      <aside className="w-64 border-r border-white/10 glass overflow-y-auto hidden md:flex flex-col">
        <div className="p-4 border-b border-white/10">
          <h1 className="font-secondary text-xl font-bold flex items-center gap-2">
            <Video className="w-5 h-5 text-pink-400" /> GAAIUS Socials
          </h1>
          <p className="text-xs text-muted-foreground mt-1">Production Social Platform</p>
        </div>

        {/* Feature Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {SOCIAL_FEATURES.map(feature => {
            const Icon = feature.icon;
            return (
              <button
                key={feature.id}
                onClick={() => setActiveTab(feature.id)}
                className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${
                  activeTab === feature.id
                    ? "bg-pink-500/20 border border-pink-500/30 text-pink-400"
                    : "hover:bg-white/5 text-muted-foreground hover:text-white"
                }`}
              >
                <Icon className="w-5 h-5" />
                <div className="text-left">
                  <p className="font-medium text-sm">{feature.label}</p>
                  <p className="text-xs text-muted-foreground/70">{feature.desc}</p>
                </div>
              </button>
            );
          })}
        </nav>

        {/* User Info */}
        <div className="p-4 border-t border-white/10">
          {user && userProfile ? (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-pink-500/20 flex items-center justify-center">
                <User className="w-5 h-5 text-pink-400" />
              </div>
              <div>
                <p className="text-sm font-medium">{userProfile.display_name || user.name}</p>
                <p className="text-xs text-muted-foreground">@{userProfile.username || 'user'}</p>
              </div>
            </div>
          ) : user ? (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-pink-500/20 flex items-center justify-center">
                <User className="w-5 h-5 text-pink-400" />
              </div>
              <div>
                <p className="text-sm font-medium">{user.name || user.email}</p>
                <p className="text-xs text-muted-foreground">Loading...</p>
              </div>
            </div>
          ) : (
            <Button onClick={showAuth} className="w-full">Sign In</Button>
          )}
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 border-b border-white/10 glass flex items-center justify-between px-6">
          <div className="flex items-center gap-4">
            <button className="md:hidden p-2 hover:bg-white/5 rounded-lg">
              <Menu className="w-5 h-5" />
            </button>
            <div>
              <h2 className="font-secondary text-lg font-semibold capitalize">{activeTab}</h2>
              <p className="text-xs text-muted-foreground">Real social platform with AI</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {user && (
              <Button onClick={() => setShowCreateModal(true)} className="bg-pink-500 hover:bg-pink-600" size="sm">
                <Plus className="w-4 h-4 mr-2" /> Create Post
              </Button>
            )}
            <button onClick={() => navigate("/")} className="p-2 hover:bg-white/5 rounded-lg">
              <X className="w-5 h-5" />
            </button>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-y-auto">
          {activeTab === "feed" && (
            <div className="max-w-2xl mx-auto p-6 space-y-6">
              {loadingFeed ? (
                <div className="text-center py-12">
                  <Loader2 className="w-8 h-8 mx-auto animate-spin text-pink-400 mb-4" />
                  <p className="text-muted-foreground">Loading feed...</p>
                </div>
              ) : socialPosts.length === 0 ? (
                <div className="text-center py-20">
                  <Video className="w-16 h-16 mx-auto text-pink-400/30 mb-4" />
                  <h3 className="text-xl font-bold mb-2">No posts yet</h3>
                  <p className="text-muted-foreground mb-6">Start by creating your first viral post</p>
                  <Button onClick={() => setShowCreateModal(true)} className="bg-pink-500 hover:bg-pink-600">
                    <Plus className="w-4 h-4 mr-2" /> Create First Post
                  </Button>
                </div>
              ) : (
                socialPosts.map(post => (
                  <div key={post._id} className="rounded-2xl bg-white/5 border border-white/10 overflow-hidden hover:border-pink-500/30 transition-all">
                    {/* Post Header */}
                    <div className="p-4 border-b border-white/10 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-pink-500/20 flex items-center justify-center">
                          <User className="w-5 h-5 text-pink-400" />
                        </div>
                        <div>
                          <p className="text-sm font-medium">{post.user?.display_name || "User"}</p>
                          <p className="text-xs text-muted-foreground">
                            {post.created_at ? new Date(post.created_at).toLocaleDateString() : "Just now"}
                          </p>
                        </div>
                      </div>
                      <button className="p-2 hover:bg-white/10 rounded-lg">⋯</button>
                    </div>

                    {/* Media */}
                    {post.media_items && post.media_items.length > 0 && (
                      <div className="aspect-square bg-black/50 flex items-center justify-center overflow-hidden">
                        {post.media_items[0].media_type === "photo" && (
                          <img src={post.media_items[0].url} alt="post" className="w-full h-full object-cover" />
                        )}
                        {(post.media_items[0].media_type === "video" || post.media_items[0].media_type === "reel") && (
                          <video
                            src={post.media_items[0].url}
                            controls
                            className="w-full h-full object-cover"
                          />
                        )}
                      </div>
                    )}

                    {/* Content */}
                    <div className="p-4">
                      <p className="text-sm leading-relaxed mb-3">{post.content}</p>
                      {post.ai_enhanced && (
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/20 border border-purple-500/30 mb-3">
                          <Sparkles className="w-3 h-3 text-purple-400" />
                          <span className="text-xs text-purple-400">AI Enhanced</span>
                        </div>
                      )}
                    </div>

                    {/* Engagement */}
                    <div className="px-4 py-2 border-t border-white/10 flex items-center justify-between text-sm">
                      <button
                        onClick={() => (post.user_liked ? unlikePost(post._id) : likePost(post._id))}
                        className="flex items-center gap-2 p-2 rounded-lg hover:bg-white/5 group"
                      >
                        <Heart
                          className={`w-4 h-4 ${post.user_liked ? "fill-pink-400 text-pink-400" : "text-muted-foreground group-hover:text-pink-400"}`}
                        />
                        {post.likes_count || 0}
                      </button>
                      <button className="flex items-center gap-2 p-2 rounded-lg hover:bg-white/5 group">
                        <MessageSquare className="w-4 h-4 text-muted-foreground group-hover:text-cyan-400" />
                        {post.comments_count || 0}
                      </button>
                      <button
                        onClick={() => repostPost(post._id)}
                        className="flex items-center gap-2 p-2 rounded-lg hover:bg-white/5 group"
                      >
                        <Share2 className="w-4 h-4 text-muted-foreground group-hover:text-green-400" />
                        {post.reposts_count || 0}
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === "create" && (
            <div className="max-w-2xl mx-auto p-6">
              <div className="rounded-2xl bg-white/5 border border-white/10 p-8">
                <h3 className="text-2xl font-bold mb-6">Create a Post</h3>

                {/* Media Type Selector */}
                <div className="grid grid-cols-3 gap-4 mb-6">
                  {[
                    { type: "photo", icon: Image, label: "Photo" },
                    { type: "video", icon: Video, label: "Video" },
                    { type: "reel", icon: Sparkles, label: "Reel" }
                  ].map(item => (
                    <button
                      key={item.type}
                      onClick={() => setMediaType(item.type)}
                      className={`p-4 rounded-xl border-2 transition-all flex flex-col items-center gap-2 ${
                        mediaType === item.type
                          ? "border-pink-500/50 bg-pink-500/10"
                          : "border-white/10 bg-white/5 hover:border-white/20"
                      }`}
                    >
                      <item.icon className="w-6 h-6" />
                      <span className="text-sm font-medium">{item.label}</span>
                    </button>
                  ))}
                </div>

                {/* Media Preview */}
                {selectedMedia && (
                  <div className="mb-6 rounded-xl overflow-hidden border border-pink-500/30 bg-black/50">
                    {selectedMedia.type === "photo" ? (
                      <img src={selectedMedia.preview} alt="preview" className="w-full h-auto max-h-96 object-contain" />
                    ) : (
                      <video src={selectedMedia.preview} controls className="w-full h-auto max-h-96" />
                    )}
                    <button
                      onClick={() => setSelectedMedia(null)}
                      className="absolute top-4 right-4 p-2 bg-red-500/80 hover:bg-red-600 rounded-lg"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                )}

                {/* File Input */}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*,video/*"
                  onChange={handleMediaSelect}
                  className="hidden"
                />

                {/* Media Upload Button */}
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full p-4 mb-6 rounded-xl border-2 border-dashed border-pink-500/30 hover:border-pink-500/50 transition-all text-center"
                >
                  <Image className="w-6 h-6 mx-auto mb-2 text-pink-400" />
                  <p className="text-sm font-medium">Click to upload media</p>
                  <p className="text-xs text-muted-foreground">or drag and drop</p>
                </button>

                {/* Content Input */}
                <textarea
                  value={draftContent}
                  onChange={(e) => setDraftContent(e.target.value)}
                  placeholder="What's on your mind? Share your thoughts, ideas, or announcements..."
                  className="w-full h-32 rounded-xl bg-white/5 border border-white/10 p-4 focus:border-pink-500/50 outline-none resize-none text-white placeholder-muted-foreground mb-6"
                />

                {/* AI Enhancement Toggle */}
                <label className="flex items-center gap-3 mb-6 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={aiEnhance}
                    onChange={(e) => setAiEnhance(e.target.checked)}
                    className="w-4 h-4 rounded"
                  />
                  <span className="text-sm flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-purple-400" />
                    Enhance with AI for maximum engagement
                  </span>
                </label>

                {/* Action Buttons */}
                <div className="flex gap-3">
                  <Button
                    onClick={createPost}
                    disabled={loading || (!draftContent.trim() && !selectedMedia)}
                    className="flex-1 bg-pink-500 hover:bg-pink-600"
                  >
                    {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
                    {loading ? "Posting..." : "Post"}
                  </Button>
                  <Button variant="outline" className="px-6">
                    Save Draft
                  </Button>
                </div>
              </div>
            </div>
          )}

          {activeTab === "messages" && (
            <div className="h-full flex">
              {/* Conversations List */}
              <div className="w-64 border-r border-white/10 overflow-y-auto p-4 space-y-2">
                <h3 className="font-bold mb-4">Messages</h3>
                <div className="p-4 rounded-lg bg-white/5 border border-white/10 cursor-pointer hover:border-pink-500/30">
                  <p className="font-medium">Start new conversation</p>
                  <p className="text-xs text-muted-foreground">Search users to message</p>
                </div>
              </div>
              {/* Chat Area */}
              <div className="flex-1 flex flex-col">
                <div className="flex-1 p-6 overflow-y-auto">
                  <div className="text-center text-muted-foreground">
                    <MessageSquare className="w-16 h-16 mx-auto text-pink-400/30 mb-4" />
                    <h3 className="text-lg font-bold mb-2">Direct Messages</h3>
                    <p>Select a conversation or start a new one</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "notifications" && (
            <div className="max-w-2xl mx-auto p-6">
              <h3 className="text-xl font-bold mb-6">Activity & Notifications</h3>
              <div className="space-y-3">
                {notifications.length === 0 ? (
                  <div className="text-center py-12">
                    <Sparkles className="w-12 h-12 mx-auto text-pink-400/30 mb-4" />
                    <p className="text-muted-foreground">No notifications yet</p>
                  </div>
                ) : (
                  notifications.map((notif, i) => (
                    <div key={i} className="p-4 rounded-xl bg-white/5 border border-white/10 hover:border-pink-500/30 transition-all">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-pink-500/20 flex items-center justify-center flex-shrink-0">
                          <Heart className="w-5 h-5 text-pink-400" />
                        </div>
                        <div className="flex-1">
                          <p className="text-sm">{notif.message}</p>
                          <p className="text-xs text-muted-foreground">
                            {notif.timestamp ? new Date(notif.timestamp).toLocaleDateString() : "Just now"}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {activeTab === "analytics" && (
            <div className="max-w-4xl mx-auto p-6">
              <h3 className="text-2xl font-bold mb-6">Your Analytics</h3>
              {analytics ? (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                  {[
                    { label: "Total Followers", value: analytics.followers_count || 0, icon: User, color: "text-cyan-400" },
                    { label: "Total Reach", value: (analytics.total_reach || 0).toLocaleString(), icon: Zap, color: "text-yellow-400" },
                    { label: "Engagement Rate", value: `${(analytics.engagement_rate || 0).toFixed(1)}%`, icon: Sparkles, color: "text-purple-400" },
                    { label: "Total Posts", value: analytics.total_posts || 0, icon: MessageSquare, color: "text-pink-400" }
                  ].map((stat, i) => {
                    const Icon = stat.icon;
                    return (
                      <div key={i} className="p-6 rounded-2xl bg-white/5 border border-white/10">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-muted-foreground text-sm mb-2">{stat.label}</p>
                            <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
                          </div>
                          <Icon className={`w-8 h-8 ${stat.color}/30`} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Loader2 className="w-8 h-8 mx-auto animate-spin text-pink-400 mb-4" />
                  <p className="text-muted-foreground">Loading analytics...</p>
                </div>
              )}
            </div>
          )}

          {activeTab === "duet-collab" && (
            <DuetCollabVideoEditor user={user} />
          )}

          {activeTab === "profile" && userProfile && (
            <div className="max-w-2xl mx-auto p-6">
              {/* Profile Header */}
              <div className="rounded-2xl bg-white/5 border border-white/10 overflow-hidden mb-6">
                {/* Banner */}
                <div className="h-32 bg-gradient-to-r from-pink-500/20 to-purple-500/20" />

                {/* Profile Info */}
                <div className="px-6 pb-6">
                  <div className="flex items-end gap-4 -mt-16 mb-6">
                    <div className="w-24 h-24 rounded-2xl bg-pink-500/20 border-4 border-[#050505] flex items-center justify-center">
                      <User className="w-12 h-12 text-pink-400" />
                    </div>
                    <div className="flex-1">
                      <h2 className="text-2xl font-bold">{userProfile.display_name || "User"}</h2>
                      <p className="text-muted-foreground">@{userProfile.username || "user"}</p>
                    </div>
                    <Button className="bg-pink-500 hover:bg-pink-600">Edit Profile</Button>
                  </div>

                  <p className="text-muted-foreground mb-6">{userProfile.bio || "No bio yet"}</p>

                  {/* Stats */}
                  <div className="grid grid-cols-4 gap-4 pt-6 border-t border-white/10">
                    {[
                      { label: "Posts", value: userProfile.posts_count || 0 },
                      { label: "Followers", value: userProfile.followers_count || 0 },
                      { label: "Following", value: userProfile.following_count || 0 },
                      { label: "Likes", value: userProfile.total_likes_received || 0 }
                    ].map((stat, i) => (
                      <div key={i} className="text-center">
                        <p className="text-2xl font-bold text-pink-400">{stat.value.toLocaleString()}</p>
                        <p className="text-xs text-muted-foreground">{stat.label}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Create Post Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className="bg-[#050505] border border-white/10 max-w-lg">
          <DialogHeader>
            <DialogTitle>Create New Post</DialogTitle>
            <DialogDescription>Share your thoughts with the world</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <textarea
              value={draftContent}
              onChange={(e) => setDraftContent(e.target.value)}
              placeholder="What's on your mind?"
              className="w-full h-24 rounded-lg bg-white/5 border border-white/10 p-3 focus:border-pink-500/50 outline-none resize-none text-white placeholder-muted-foreground"
            />
            <div className="flex gap-2">
              <Button
                onClick={createPost}
                disabled={loading}
                className="flex-1 bg-pink-500 hover:bg-pink-600"
              >
                {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Plus className="w-4 h-4 mr-2" />}
                Post
              </Button>
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Main App Component
const MainApp = () => {
  // Persist mode in localStorage
  const [mode, setMode] = useState(() => {
    const savedMode = localStorage.getItem("gaaius_mode");
    return savedMode || "chat";
  });
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [generations, setGenerations] = useState([]);
  const [videoStyle, setVideoStyle] = useState("cinematic");
  const [fileType, setFileType] = useState("code");
  const [showAuth, setShowAuth] = useState(false);
  const [showPro, setShowPro] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [showVideoAd, setShowVideoAd] = useState(false);
  const [generationCount, setGenerationCount] = useState(() => {
    return parseInt(localStorage.getItem("gaaius_gen_count") || "0");
  });
  const [lastAdTime, setLastAdTime] = useState(() => {
    return parseInt(localStorage.getItem("gaaius_last_ad") || Date.now().toString());
  });
  
  const { user, token, logout } = useAuthStore();
  const messagesEndRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const inputRef = useRef(null);
  const navigate = useNavigate();
  const location = useLocation();

  // Check if ad should be shown (every 10 generations or every 30 minutes)
  const shouldShowAd = () => {
    if (user?.is_pro) return false; // Pro users never see ads
    
    const now = Date.now();
    const thirtyMinutes = 30 * 60 * 1000;
    const timeSinceLastAd = now - lastAdTime;
    
    // Show ad if 30 minutes passed
    if (timeSinceLastAd >= thirtyMinutes) {
      return true;
    }
    
    // Show ad every 10 generations
    if (generationCount > 0 && generationCount % 10 === 0) {
      return true;
    }
    
    return false;
  };

  // Increment generation count and check for ad
  const trackGeneration = () => {
    if (user?.is_pro) return; // Pro users don't track
    
    const newCount = generationCount + 1;
    setGenerationCount(newCount);
    localStorage.setItem("gaaius_gen_count", newCount.toString());
    
    if (shouldShowAd() || newCount % 10 === 0) {
      setShowVideoAd(true);
      setLastAdTime(Date.now());
      localStorage.setItem("gaaius_last_ad", Date.now().toString());
    }
  };

  // 30-minute timer for ads
  useEffect(() => {
    if (user?.is_pro) return; // Pro users skip timer
    
    const checkAdTimer = setInterval(() => {
      const now = Date.now();
      const thirtyMinutes = 30 * 60 * 1000;
      const timeSinceLastAd = now - lastAdTime;
      
      if (timeSinceLastAd >= thirtyMinutes) {
        setShowVideoAd(true);
        setLastAdTime(now);
        localStorage.setItem("gaaius_last_ad", now.toString());
      }
    }, 60000); // Check every minute
    
    return () => clearInterval(checkAdTimer);
  }, [user?.is_pro, lastAdTime]);

  // Save mode to localStorage when it changes
  useEffect(() => {
    localStorage.setItem("gaaius_mode", mode);
  }, [mode]);

  // Handle mode change with navigation
  const handleModeChange = (newMode) => {
    setMode(newMode);
    if (newMode === "marketplace") {
      navigate("/marketplace");
    } else if (newMode === "ads") {
      navigate("/ads");
    } else if (newMode === "socials") {
      navigate("/socials");
    } else if (newMode === "imageResizer") {
      navigate("/image-resizer");
    } else if (newMode === "imageConverter") {
      navigate("/image-converter");
    } else if (newMode === "multiTube") {
      navigate("/multitube");
    } else if (newMode === "music") {
      navigate("/music");
    } else if (newMode === "aiFilterStudio") {
      navigate("/ai-filter-studio");
    } else if (location.pathname !== "/") {
      navigate("/");
    }
  };

  // Check auth on mount
  useEffect(() => {
    if (token) {
      api.get("/auth/me").then(res => useAuthStore.getState().setUser(res.data)).catch(() => useAuthStore.getState().logout());
    }
  }, [token]);

  useEffect(() => { fetchSessions(); fetchGenerations(); }, []);
  useEffect(() => { if (currentSession) fetchMessages(currentSession.id); }, [currentSession]);
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const fetchSessions = async () => {
    try {
      const res = await api.get("/sessions");
      setSessions(res.data);
      if (res.data.length > 0 && !currentSession) setCurrentSession(res.data[0]);
    } catch (error) {}
  };

  const fetchMessages = async (sessionId) => {
    try {
      const res = await api.get(`/chat/${sessionId}/history`);
      setMessages(res.data);
    } catch (error) {}
  };

  const fetchGenerations = async () => {
    try {
      const res = await api.get("/generations");
      setGenerations(res.data);
    } catch (error) {}
  };

  const createSession = async () => {
    try {
      const res = await api.post("/sessions?name=New Chat");
      setSessions(prev => [res.data, ...prev]);
      setCurrentSession(res.data);
      setMessages([]);
      toast.success("New chat created");
    } catch (error) {
      toast.error("Failed to create session");
    }
  };

  const deleteSession = async (sessionId) => {
    try {
      await api.delete(`/sessions/${sessionId}`);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      if (currentSession?.id === sessionId) {
        const remaining = sessions.filter(s => s.id !== sessionId);
        setCurrentSession(remaining[0] || null);
      }
      toast.success("Chat deleted");
    } catch (error) {
      toast.error("Failed to delete session");
    }
  };

  // Check for projects/build routes
  if (location.pathname === "/projects") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <div className="h-screen flex bg-[#050505] overflow-hidden">
          <Toaster position="top-center" theme="dark" />
          <Sidebar 
            mode={mode} setMode={handleModeChange} sessions={sessions} currentSession={currentSession}
            setCurrentSession={setCurrentSession} setSidebarOpen={setSidebarOpen} sidebarOpen={sidebarOpen}
            createSession={createSession} deleteSession={deleteSession} navigate={navigate}
            user={user} showAuth={() => setShowAuth(true)} showPro={() => setShowPro(true)} 
            showProfile={() => setShowProfile(true)} logout={logout}
          />
          {sidebarOpen && <div className="fixed inset-0 bg-black/50 z-40 md:hidden" onClick={() => setSidebarOpen(false)} />}
          <main className="flex-1 flex flex-col min-w-0">
            <header className="h-16 border-b border-white/10 flex items-center justify-between px-4 md:px-6 glass">
              <div className="flex items-center gap-4">
                <button className="md:hidden p-2 hover:bg-white/5 rounded-lg" onClick={() => setSidebarOpen(true)}><Menu className="w-5 h-5" /></button>
                <span className="font-secondary text-sm font-semibold">Projects</span>
              </div>
            </header>
            <div className="flex-1 overflow-auto"><ProjectsPage /></div>
          </main>
        </div>
      </>
    );
  }

  if (location.pathname === "/build") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <div className="h-screen bg-[#050505]">
          <Toaster position="top-center" theme="dark" />
          <BuildPage navigate={navigate} user={user} showAuth={() => setShowAuth(true)} showPro={() => setShowPro(true)} showProfile={() => setShowProfile(true)} logout={logout} />
        </div>
      </>
    );
  }

  if (location.pathname === "/documents") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <div className="h-screen bg-[#050505]">
          <Toaster position="top-center" theme="dark" />
          <DocumentStudio onBack={() => navigate("/")} />
        </div>
      </>
    );
  }

  // Marketplace Component - Independent Platform
  const MarketplaceBuilder = () => {
    const [listings, setListings] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [formData, setFormData] = useState({ title: "", description: "", price: "", category: "" });

    const loadListings = async () => {
      setLoading(true);
      try {
        const response = await api.get("/marketplace/listings");
        setListings(response.data.listings || []);
      } catch (error) {
        console.error("Error loading marketplace:", error);
        toast.error("Failed to load marketplace");
      } finally {
        setLoading(false);
      }
    };

    useEffect(() => {
      loadListings();
    }, []);

    const createListing = async () => {
      if (!formData.title || !formData.price) {
        toast.error("Please fill in required fields");
        return;
      }
      try {
        const response = await api.post("/marketplace/listings", {
          title: formData.title,
          description: formData.description,
          price_usd: parseFloat(formData.price),
          category: formData.category
        });
        setListings(prev => [response.data, ...prev]);
        setFormData({ title: "", description: "", price: "", category: "" });
        setShowCreateForm(false);
        toast.success("Listing created!");
      } catch (error) {
        toast.error("Failed to create listing");
      }
    };

    return (
      <div className="h-screen bg-[#050505] flex flex-col overflow-hidden">
        <div className="h-16 border-b border-emerald-500/20 flex items-center justify-between px-6 glass">
          <div className="flex items-center gap-3">
            <ShoppingCart className="w-6 h-6 text-emerald-400" />
            <h1 className="text-xl font-bold">Marketplace</h1>
          </div>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 rounded-lg transition"
          >
            <Plus className="w-4 h-4" />
            Create Listing
          </button>
        </div>

        <div className="flex-1 overflow-auto p-6">
          {showCreateForm && (
            <div className="mb-6 p-4 bg-emerald-600/10 border border-emerald-500/30 rounded-lg">
              <h3 className="text-lg font-semibold mb-3">New Listing</h3>
              <div className="space-y-3">
                <input
                  type="text"
                  placeholder="Title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-2 bg-black/30 border border-emerald-500/30 rounded text-white placeholder-gray-400"
                />
                <textarea
                  placeholder="Description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 bg-black/30 border border-emerald-500/30 rounded text-white placeholder-gray-400 h-20"
                />
                <input
                  type="text"
                  placeholder="Category"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full px-3 py-2 bg-black/30 border border-emerald-500/30 rounded text-white placeholder-gray-400"
                />
                <input
                  type="number"
                  placeholder="Price (USD)"
                  value={formData.price}
                  onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                  className="w-full px-3 py-2 bg-black/30 border border-emerald-500/30 rounded text-white placeholder-gray-400"
                />
                <button
                  onClick={createListing}
                  className="w-full px-4 py-2 bg-emerald-600 hover:bg-emerald-700 rounded transition"
                >
                  Create Listing
                </button>
              </div>
            </div>
          )}

          {loading ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="w-8 h-8 animate-spin text-emerald-400" />
            </div>
          ) : listings.length === 0 ? (
            <div className="text-center text-gray-400 py-12">No listings yet. Create one to get started!</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {listings.map((listing) => (
                <div key={listing._id} className="p-4 bg-emerald-600/10 border border-emerald-500/30 rounded-lg hover:border-emerald-500/60 transition">
                  <h3 className="font-semibold text-lg mb-2">{listing.title}</h3>
                  <p className="text-sm text-gray-300 mb-2">{listing.description}</p>
                  <div className="flex justify-between items-center">
                    <span className="text-emerald-400 font-bold">${listing.price_usd}</span>
                    <span className="text-xs text-gray-400">{listing.category}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  // Ads Component - Independent Platform
  const AdsBuilder = () => {
    const [campaigns, setCampaigns] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [formData, setFormData] = useState({ headline: "", budget: "", interests: "" });

    const loadCampaigns = async () => {
      setLoading(true);
      try {
        const response = await api.get("/ads/campaigns");
        setCampaigns(response.data.campaigns || []);
      } catch (error) {
        console.error("Error loading campaigns:", error);
        toast.error("Failed to load campaigns");
      } finally {
        setLoading(false);
      }
    };

    useEffect(() => {
      loadCampaigns();
    }, []);

    const createCampaign = async () => {
      if (!formData.headline || !formData.budget) {
        toast.error("Please fill in required fields");
        return;
      }
      try {
        const response = await api.post("/ads/campaigns", {
          headline: formData.headline,
          budget: parseFloat(formData.budget),
          targeting: { interests: formData.interests.split(",").map(i => i.trim()) }
        });
        setCampaigns(prev => [response.data, ...prev]);
        setFormData({ headline: "", budget: "", interests: "" });
        setShowCreateForm(false);
        toast.success("Campaign created!");
      } catch (error) {
        toast.error("Failed to create campaign");
      }
    };

    return (
      <div className="h-screen bg-[#050505] flex flex-col overflow-hidden">
        <div className="h-16 border-b border-amber-500/20 flex items-center justify-between px-6 glass">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-6 h-6 text-amber-400" />
            <h1 className="text-xl font-bold">Ad Campaigns</h1>
          </div>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 rounded-lg transition"
          >
            <Plus className="w-4 h-4" />
            Create Campaign
          </button>
        </div>

        <div className="flex-1 overflow-auto p-6">
          {showCreateForm && (
            <div className="mb-6 p-4 bg-amber-600/10 border border-amber-500/30 rounded-lg">
              <h3 className="text-lg font-semibold mb-3">New Ad Campaign</h3>
              <div className="space-y-3">
                <input
                  type="text"
                  placeholder="Headline"
                  value={formData.headline}
                  onChange={(e) => setFormData({ ...formData, headline: e.target.value })}
                  className="w-full px-3 py-2 bg-black/30 border border-amber-500/30 rounded text-white placeholder-gray-400"
                />
                <input
                  type="number"
                  placeholder="Budget (USD)"
                  value={formData.budget}
                  onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
                  className="w-full px-3 py-2 bg-black/30 border border-amber-500/30 rounded text-white placeholder-gray-400"
                />
                <input
                  type="text"
                  placeholder="Interests (comma separated)"
                  value={formData.interests}
                  onChange={(e) => setFormData({ ...formData, interests: e.target.value })}
                  className="w-full px-3 py-2 bg-black/30 border border-amber-500/30 rounded text-white placeholder-gray-400"
                />
                <button
                  onClick={createCampaign}
                  className="w-full px-4 py-2 bg-amber-600 hover:bg-amber-700 rounded transition"
                >
                  Create Campaign
                </button>
              </div>
            </div>
          )}

          {loading ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="w-8 h-8 animate-spin text-amber-400" />
            </div>
          ) : campaigns.length === 0 ? (
            <div className="text-center text-gray-400 py-12">No campaigns yet. Create one to get started!</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {campaigns.map((campaign) => (
                <div key={campaign._id} className="p-4 bg-amber-600/10 border border-amber-500/30 rounded-lg hover:border-amber-500/60 transition">
                  <h3 className="font-semibold text-lg mb-2">{campaign.headline}</h3>
                  <div className="space-y-2 text-sm text-gray-300">
                    <p>Budget: <span className="text-amber-400 font-bold">${campaign.budget}</span></p>
                    <p>Status: <span className="text-amber-400">{campaign.status || "Active"}</span></p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  // Image Resizer Component - Advanced Image Resizing Tool
  const ImageResizerBuilder = () => {
    const [selectedImage, setSelectedImage] = useState(null);
    const [preview, setPreview] = useState(null);
    const [resizeSettings, setResizeSettings] = useState({ width: 800, height: 600, aspectRatio: true, format: "original" });
    const [resizing, setResizing] = useState(false);
    const [history, setHistory] = useState([]);

    const handleImageSelect = (e) => {
      const file = e.target.files?.[0];
      if (!file) return;
      
      if (!file.type.startsWith('image/')) {
        toast.error('Please select a valid image file');
        return;
      }

      if (file.size > 50 * 1024 * 1024) {
        toast.error('Image size must be less than 50MB');
        return;
      }

      setSelectedImage(file);
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);
    };

    const handleResize = async () => {
      if (!selectedImage) {
        toast.error('Please select an image first');
        return;
      }

      setResizing(true);
      try {
        const formData = new FormData();
        formData.append('image', selectedImage);
        formData.append('width', resizeSettings.width);
        formData.append('height', resizeSettings.height);
        formData.append('aspectRatio', resizeSettings.aspectRatio);
        formData.append('format', resizeSettings.format);

        const response = await api.post('/image/resize', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });

        const resizedUrl = response.data.url || response.data.image_url;
        setHistory(prev => [{ ...response.data, timestamp: new Date() }, ...prev]);
        toast.success('Image resized successfully!');

        // Auto download
        const a = document.createElement('a');
        a.href = resizedUrl;
        a.download = `resized-${Date.now()}.${resizeSettings.format || 'png'}`;
        a.click();
      } catch (error) {
        toast.error('Failed to resize image: ' + (error.response?.data?.detail || error.message));
      } finally {
        setResizing(false);
      }
    };

    return (
      <div className="h-screen bg-[#050505] flex flex-col overflow-hidden">
        <div className="h-16 border-b border-blue-500/20 flex items-center justify-between px-6 glass">
          <div className="flex items-center gap-3">
            <Wand2 className="w-6 h-6 text-blue-400" />
            <h1 className="text-xl font-bold">AI Image Resizer</h1>
          </div>
          <span className="text-xs text-gray-400">Professional Image Resizing</span>
        </div>

        <div className="flex-1 overflow-auto p-6">
          <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Upload & Preview */}
            <div className="flex flex-col gap-4">
              <div className="p-6 bg-blue-600/10 border border-blue-500/30 rounded-lg">
                <label className="cursor-pointer flex flex-col items-center justify-center py-12 hover:bg-blue-500/5 transition rounded-lg border-2 border-dashed border-blue-500/50">
                  <FileImage className="w-12 h-12 text-blue-400 mb-2" />
                  <span className="text-white font-medium">Upload Image</span>
                  <span className="text-xs text-gray-400 mt-1">Up to 50MB</span>
                  <input type="file" accept="image/*" onChange={handleImageSelect} className="hidden" />
                </label>
              </div>

              {preview && (
                <div className="p-4 bg-black/30 border border-blue-500/30 rounded-lg">
                  <p className="text-sm text-gray-400 mb-2">Preview</p>
                  <img src={preview} alt="Preview" className="w-full h-64 object-contain rounded" />
                </div>
              )}
            </div>

            {/* Settings */}
            <div className="flex flex-col gap-4">
              <div className="p-4 bg-blue-600/10 border border-blue-500/30 rounded-lg space-y-4">
                <h3 className="text-lg font-semibold">Resize Settings</h3>
                
                <div>
                  <label className="text-sm text-gray-300 block mb-2">Width (px)</label>
                  <input
                    type="number"
                    value={resizeSettings.width}
                    onChange={(e) => setResizeSettings({ ...resizeSettings, width: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 bg-black/30 border border-blue-500/30 rounded text-white"
                  />
                </div>

                <div>
                  <label className="text-sm text-gray-300 block mb-2">Height (px)</label>
                  <input
                    type="number"
                    value={resizeSettings.height}
                    onChange={(e) => setResizeSettings({ ...resizeSettings, height: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 bg-black/30 border border-blue-500/30 rounded text-white"
                  />
                </div>

                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={resizeSettings.aspectRatio}
                    onChange={(e) => setResizeSettings({ ...resizeSettings, aspectRatio: e.target.checked })}
                    className="w-4 h-4"
                  />
                  <span className="text-gray-300">Lock Aspect Ratio</span>
                </label>

                <div>
                  <label className="text-sm text-gray-300 block mb-2">Output Format</label>
                  <select
                    value={resizeSettings.format}
                    onChange={(e) => setResizeSettings({ ...resizeSettings, format: e.target.value })}
                    className="w-full px-3 py-2 bg-black/30 border border-blue-500/30 rounded text-white"
                  >
                    <option value="original">Original Format</option>
                    <option value="jpg">JPEG</option>
                    <option value="png">PNG</option>
                    <option value="webp">WebP</option>
                    <option value="gif">GIF</option>
                  </select>
                </div>

                <button
                  onClick={handleResize}
                  disabled={!preview || resizing}
                  className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg transition flex items-center justify-center gap-2"
                >
                  {resizing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
                  {resizing ? 'Resizing...' : 'Resize Image'}
                </button>
              </div>

              {/* History */}
              {history.length > 0 && (
                <div className="p-4 bg-black/30 border border-blue-500/30 rounded-lg">
                  <p className="text-sm text-gray-400 mb-3">Recent Resizes</p>
                  <div className="space-y-2 max-h-40 overflow-auto">
                    {history.map((item, i) => (
                      <div key={i} className="text-xs text-gray-400 p-2 bg-black/30 rounded">
                        {item.width}x{item.height} - {new Date(item.timestamp).toLocaleTimeString()}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Image Converter Component - Multi-Format Image Conversion
  const ImageConverterBuilder = () => {
    const [selectedImage, setSelectedImage] = useState(null);
    const [preview, setPreview] = useState(null);
    const [targetFormat, setTargetFormat] = useState('png');
    const [quality, setQuality] = useState(90);
    const [converting, setConverting] = useState(false);
    const [conversions, setConversions] = useState([]);

    const SUPPORTED_FORMATS = [
      { value: 'jpg', label: 'JPEG (.jpg)' },
      { value: 'png', label: 'PNG (.png)' },
      { value: 'webp', label: 'WebP (.webp)' },
      { value: 'gif', label: 'GIF (.gif)' },
      { value: 'bmp', label: 'BMP (.bmp)' },
      { value: 'tiff', label: 'TIFF (.tiff)' },
      { value: 'ico', label: 'Icon (.ico)' }
    ];

    const handleImageSelect = (e) => {
      const file = e.target.files?.[0];
      if (!file) return;

      if (!file.type.startsWith('image/')) {
        toast.error('Please select a valid image file');
        return;
      }

      if (file.size > 50 * 1024 * 1024) {
        toast.error('Image size must be less than 50MB');
        return;
      }

      setSelectedImage(file);
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);
    };

    const handleConvert = async () => {
      if (!selectedImage) {
        toast.error('Please select an image first');
        return;
      }

      setConverting(true);
      try {
        const formData = new FormData();
        formData.append('image', selectedImage);
        formData.append('format', targetFormat);
        formData.append('quality', quality);

        const response = await api.post('/image/convert', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });

        const convertedUrl = response.data.url || response.data.image_url;
        setConversions(prev => [{ ...response.data, timestamp: new Date() }, ...prev]);
        toast.success(`Image converted to ${targetFormat.toUpperCase()}!`);

        // Auto download
        const a = document.createElement('a');
        a.href = convertedUrl;
        a.download = `converted-${Date.now()}.${targetFormat}`;
        a.click();
      } catch (error) {
        toast.error('Conversion failed: ' + (error.response?.data?.detail || error.message));
      } finally {
        setConverting(false);
      }
    };

    return (
      <div className="h-screen bg-[#050505] flex flex-col overflow-hidden">
        <div className="h-16 border-b border-indigo-500/20 flex items-center justify-between px-6 glass">
          <div className="flex items-center gap-3">
            <FileImage className="w-6 h-6 text-indigo-400" />
            <h1 className="text-xl font-bold">AI Image Converter</h1>
          </div>
          <span className="text-xs text-gray-400">Convert to Any Format</span>
        </div>

        <div className="flex-1 overflow-auto p-6">
          <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Upload & Preview */}
            <div className="flex flex-col gap-4">
              <div className="p-6 bg-indigo-600/10 border border-indigo-500/30 rounded-lg">
                <label className="cursor-pointer flex flex-col items-center justify-center py-12 hover:bg-indigo-500/5 transition rounded-lg border-2 border-dashed border-indigo-500/50">
                  <FileImage className="w-12 h-12 text-indigo-400 mb-2" />
                  <span className="text-white font-medium">Upload Image</span>
                  <span className="text-xs text-gray-400 mt-1">Support most formats</span>
                  <input type="file" accept="image/*" onChange={handleImageSelect} className="hidden" />
                </label>
              </div>

              {preview && (
                <div className="p-4 bg-black/30 border border-indigo-500/30 rounded-lg">
                  <p className="text-sm text-gray-400 mb-2">Original Preview</p>
                  <img src={preview} alt="Preview" className="w-full h-64 object-contain rounded" />
                </div>
              )}
            </div>

            {/* Format Selection & Settings */}
            <div className="flex flex-col gap-4">
              <div className="p-4 bg-indigo-600/10 border border-indigo-500/30 rounded-lg space-y-4">
                <h3 className="text-lg font-semibold">Conversion Settings</h3>

                <div>
                  <label className="text-sm text-gray-300 block mb-2">Target Format</label>
                  <div className="grid grid-cols-2 gap-2">
                    {SUPPORTED_FORMATS.map(fmt => (
                      <button
                        key={fmt.value}
                        onClick={() => setTargetFormat(fmt.value)}
                        className={`px-3 py-2 rounded text-sm transition ${
                          targetFormat === fmt.value
                            ? 'bg-indigo-600 text-white'
                            : 'bg-black/30 border border-indigo-500/30 text-gray-300 hover:border-indigo-500/60'
                        }`}
                      >
                        {fmt.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-sm text-gray-300 block mb-2">Quality: {quality}%</label>
                  <input
                    type="range"
                    min="10"
                    max="100"
                    value={quality}
                    onChange={(e) => setQuality(parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>

                <button
                  onClick={handleConvert}
                  disabled={!preview || converting}
                  className="w-full px-4 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-lg transition flex items-center justify-center gap-2"
                >
                  {converting ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileImage className="w-4 h-4" />}
                  {converting ? 'Converting...' : 'Convert Image'}
                </button>
              </div>

              {/* Conversion History */}
              {conversions.length > 0 && (
                <div className="p-4 bg-black/30 border border-indigo-500/30 rounded-lg">
                  <p className="text-sm text-gray-400 mb-3">Conversion History</p>
                  <div className="space-y-2 max-h-40 overflow-auto">
                    {conversions.map((item, i) => (
                      <div key={i} className="text-xs text-gray-400 p-2 bg-black/30 rounded">
                        → {item.format?.toUpperCase()} - {new Date(item.timestamp).toLocaleTimeString()}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // MultiTube Component - Video Upload & Streaming Platform
  const MultiTubeBuilder = () => {
    const [videos, setVideos] = useState([]);
    const [selectedVideo, setSelectedVideo] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [showUploadForm, setShowUploadForm] = useState(false);
    const [formData, setFormData] = useState({ title: '', description: '', tags: '', thumbnail: null });
    const [searchQuery, setSearchQuery] = useState('');
    const [viewMode, setViewMode] = useState('grid');

    useEffect(() => {
      loadVideos();
    }, []);

    const loadVideos = async () => {
      try {
        const response = await api.get('/multitube/videos');
        setVideos(response.data.videos || []);
      } catch (error) {
        console.error('Error loading videos:', error);
      }
    };

    const handleVideoSelect = (e) => {
      const file = e.target.files?.[0];
      if (!file) return;

      if (!file.type.startsWith('video/')) {
        toast.error('Please select a valid video file');
        return;
      }

      if (file.size > 500 * 1024 * 1024) {
        toast.error('Video size must be less than 500MB');
        return;
      }

      setFormData(prev => ({ ...prev, video: file }));
    };

    const handleUpload = async () => {
      if (!formData.video || !formData.title) {
        toast.error('Please select a video and enter a title');
        return;
      }

      setUploading(true);
      setUploadProgress(0);

      try {
        const data = new FormData();
        data.append('video', formData.video);
        data.append('title', formData.title);
        data.append('description', formData.description);
        data.append('tags', formData.tags);
        if (formData.thumbnail) data.append('thumbnail', formData.thumbnail);

        const response = await api.post('/multitube/upload', data, {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (e) => setUploadProgress(Math.round((e.loaded / e.total) * 100))
        });

        setVideos(prev => [response.data, ...prev]);
        setFormData({ title: '', description: '', tags: '', thumbnail: null });
        setShowUploadForm(false);
        toast.success('Video uploaded successfully!');
      } catch (error) {
        toast.error('Upload failed: ' + (error.response?.data?.detail || error.message));
      } finally {
        setUploading(false);
        setUploadProgress(0);
      }
    };

    const filteredVideos = videos.filter(v => 
      v.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      v.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    );

    return (
      <div className="h-screen bg-[#050505] flex flex-col overflow-hidden">
        <div className="h-16 border-b border-red-500/20 flex items-center justify-between px-6 glass">
          <div className="flex items-center gap-3">
            <Film className="w-6 h-6 text-red-400" />
            <h1 className="text-xl font-bold">MultiTube - Video Platform</h1>
          </div>
          <button
            onClick={() => setShowUploadForm(!showUploadForm)}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition"
          >
            <Plus className="w-4 h-4" />
            Upload Video
          </button>
        </div>

        <div className="flex-1 overflow-auto">
          <div className="p-6">
            {/* Upload Form */}
            {showUploadForm && (
              <div className="mb-6 p-6 bg-red-600/10 border border-red-500/30 rounded-lg space-y-4">
                <h3 className="text-lg font-semibold">Upload New Video</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm text-gray-300 block mb-2">Video File</label>
                    <input
                      type="file"
                      accept="video/*"
                      onChange={handleVideoSelect}
                      disabled={uploading}
                      className="w-full px-3 py-2 bg-black/30 border border-red-500/30 rounded text-white"
                    />
                  </div>

                  <div>
                    <label className="text-sm text-gray-300 block mb-2">Thumbnail (Optional)</label>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={(e) => setFormData(prev => ({ ...prev, thumbnail: e.target.files?.[0] }))}
                      disabled={uploading}
                      className="w-full px-3 py-2 bg-black/30 border border-red-500/30 rounded text-white"
                    />
                  </div>

                  <div>
                    <label className="text-sm text-gray-300 block mb-2">Title *</label>
                    <input
                      type="text"
                      placeholder="Video title"
                      value={formData.title}
                      onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                      disabled={uploading}
                      className="w-full px-3 py-2 bg-black/30 border border-red-500/30 rounded text-white placeholder-gray-500"
                    />
                  </div>

                  <div>
                    <label className="text-sm text-gray-300 block mb-2">Tags (comma separated)</label>
                    <input
                      type="text"
                      placeholder="gaming, tutorial, music"
                      value={formData.tags}
                      onChange={(e) => setFormData(prev => ({ ...prev, tags: e.target.value }))}
                      disabled={uploading}
                      className="w-full px-3 py-2 bg-black/30 border border-red-500/30 rounded text-white placeholder-gray-500"
                    />
                  </div>
                </div>

                <textarea
                  placeholder="Video description"
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  disabled={uploading}
                  className="w-full px-3 py-2 bg-black/30 border border-red-500/30 rounded text-white placeholder-gray-500 h-20"
                />

                {uploading && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Uploading...</span>
                      <span>{uploadProgress}%</span>
                    </div>
                    <div className="w-full bg-black/30 rounded-full h-2">
                      <div
                        className="bg-red-600 h-2 rounded-full transition-all"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                  </div>
                )}

                <div className="flex gap-2">
                  <button
                    onClick={handleUpload}
                    disabled={uploading || !formData.video}
                    className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 rounded transition"
                  >
                    {uploading ? 'Uploading...' : 'Upload'}
                  </button>
                  <button
                    onClick={() => setShowUploadForm(false)}
                    disabled={uploading}
                    className="flex-1 px-4 py-2 bg-black/30 hover:bg-black/50 border border-red-500/30 rounded transition"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {/* Search & View Mode */}
            <div className="mb-6 flex gap-4 items-center">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search videos by title or tags..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-black/30 border border-red-500/30 rounded text-white placeholder-gray-500"
                />
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded transition ${viewMode === 'grid' ? 'bg-red-600' : 'bg-black/30 hover:bg-black/50'}`}
                >
                  <Grid className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded transition ${viewMode === 'list' ? 'bg-red-600' : 'bg-black/30 hover:bg-black/50'}`}
                >
                  <ListIcon className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Videos Display */}
            {filteredVideos.length === 0 ? (
              <div className="text-center text-gray-400 py-12">
                {videos.length === 0 ? 'No videos yet. Upload one to get started!' : 'No videos match your search.'}
              </div>
            ) : (
              <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-4'}>
                {filteredVideos.map((video) => (
                  <div
                    key={video._id}
                    onClick={() => setSelectedVideo(video)}
                    className="p-4 bg-red-600/10 border border-red-500/30 rounded-lg hover:border-red-500/60 transition cursor-pointer"
                  >
                    {video.thumbnail_url && (
                      <img src={video.thumbnail_url} alt={video.title} className="w-full h-32 object-cover rounded mb-3" />
                    )}
                    <h3 className="font-semibold text-white mb-1">{video.title}</h3>
                    <p className="text-xs text-gray-400 mb-2 line-clamp-2">{video.description}</p>
                    <div className="flex justify-between items-center text-xs text-gray-400">
                      <span>{video.views || 0} views</span>
                      <span>{new Date(video.created_at).toLocaleDateString()}</span>
                    </div>
                    {video.tags && video.tags.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {video.tags.slice(0, 3).map((tag, i) => (
                          <span key={i} className="text-xs bg-red-500/20 text-red-300 px-2 py-1 rounded">
                            #{tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Music Builder Component - Spotify & YouTube Music Clone
  const MusicBuilder = () => {
    const [tracks, setTracks] = useState([]);
    const [playlists, setPlaylists] = useState([]);
    const [currentTrack, setCurrentTrack] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [loading, setLoading] = useState(false);
    const [showUploadForm, setShowUploadForm] = useState(false);
    const [showPlaylistForm, setShowPlaylistForm] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [formData, setFormData] = useState({ title: '', artist: '', album: '', file: null });
    const [playlistName, setPlaylistName] = useState('');
    const [currentPlaylist, setCurrentPlaylist] = useState(null);
    const [queue, setQueue] = useState([]);
    const audioRef = useRef(null);

    useEffect(() => {
      loadTracks();
      loadPlaylists();
    }, []);

    const loadTracks = async () => {
      setLoading(true);
      try {
        const response = await api.get('/music/tracks');
        setTracks(response.data.tracks || []);
      } catch (error) {
        console.error('Error loading tracks:', error);
      } finally {
        setLoading(false);
      }
    };

    const loadPlaylists = async () => {
      try {
        const response = await api.get('/music/playlists');
        setPlaylists(response.data.playlists || []);
      } catch (error) {
        console.error('Error loading playlists:', error);
      }
    };

    const handleUploadTrack = async () => {
      if (!formData.file || !formData.title || !formData.artist) {
        toast.error('Please fill in all required fields');
        return;
      }

      try {
        const data = new FormData();
        data.append('file', formData.file);
        data.append('title', formData.title);
        data.append('artist', formData.artist);
        data.append('album', formData.album);

        const response = await api.post('/music/upload', data, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });

        setTracks(prev => [response.data, ...prev]);
        setFormData({ title: '', artist: '', album: '', file: null });
        setShowUploadForm(false);
        toast.success('Track uploaded successfully!');
      } catch (error) {
        toast.error('Upload failed: ' + (error.response?.data?.detail || error.message));
      }
    };

    const handleCreatePlaylist = async () => {
      if (!playlistName.trim()) {
        toast.error('Please enter a playlist name');
        return;
      }

      try {
        const response = await api.post('/music/playlists', { name: playlistName });
        setPlaylists(prev => [response.data, ...prev]);
        setPlaylistName('');
        setShowPlaylistForm(false);
        toast.success('Playlist created!');
      } catch (error) {
        toast.error('Failed to create playlist');
      }
    };

    const handlePlayTrack = (track) => {
      setCurrentTrack(track);
      setQueue(tracks);
      setIsPlaying(true);
    };

    const handleAddToPlaylist = async (playlistId) => {
      if (!currentTrack) return;
      try {
        await api.post(`/music/playlists/${playlistId}/tracks`, { track_id: currentTrack._id });
        toast.success('Track added to playlist!');
      } catch (error) {
        toast.error('Failed to add track');
      }
    };

    const filteredTracks = tracks.filter(t =>
      t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.artist.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
      <div className="h-screen bg-[#050505] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="h-16 border-b border-green-500/20 flex items-center justify-between px-6 glass">
          <div className="flex items-center gap-3">
            <ListMusic className="w-6 h-6 text-green-400" />
            <h1 className="text-xl font-bold">Music Streaming</h1>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setShowPlaylistForm(!showPlaylistForm)}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition text-sm"
            >
              <Plus className="w-4 h-4" />
              New Playlist
            </button>
            <button
              onClick={() => setShowUploadForm(!showUploadForm)}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition text-sm"
            >
              <Plus className="w-4 h-4" />
              Upload
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-hidden flex">
          {/* Sidebar - Playlists */}
          <div className="w-64 border-r border-green-500/20 bg-black/50 overflow-auto p-4 flex flex-col gap-4">
            <div>
              <p className="text-xs text-gray-400 uppercase mb-2">Playlists</p>
              <div className="space-y-1 max-h-96 overflow-auto">
                {playlists.map((playlist) => (
                  <button
                    key={playlist._id}
                    onClick={() => setCurrentPlaylist(playlist._id)}
                    className={`w-full text-left px-3 py-2 rounded text-sm transition ${
                      currentPlaylist === playlist._id
                        ? 'bg-green-600 text-white'
                        : 'text-gray-300 hover:bg-green-500/20'
                    }`}
                  >
                    {playlist.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Recently Played */}
            <div>
              <p className="text-xs text-gray-400 uppercase mb-2">Recently Played</p>
              <div className="space-y-1 text-xs text-gray-400">
                {queue.slice(0, 5).map((track) => (
                  <div key={track._id} className="truncate text-gray-500">
                    {track.title}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 overflow-auto p-6">
            {/* Upload Form */}
            {showUploadForm && (
              <div className="mb-6 p-6 bg-green-600/10 border border-green-500/30 rounded-lg space-y-4">
                <h3 className="text-lg font-semibold">Upload Music</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <input
                    type="text"
                    placeholder="Track Title *"
                    value={formData.title}
                    onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                    className="px-3 py-2 bg-black/30 border border-green-500/30 rounded text-white placeholder-gray-500"
                  />
                  <input
                    type="text"
                    placeholder="Artist *"
                    value={formData.artist}
                    onChange={(e) => setFormData(prev => ({ ...prev, artist: e.target.value }))}
                    className="px-3 py-2 bg-black/30 border border-green-500/30 rounded text-white placeholder-gray-500"
                  />
                  <input
                    type="text"
                    placeholder="Album"
                    value={formData.album}
                    onChange={(e) => setFormData(prev => ({ ...prev, album: e.target.value }))}
                    className="px-3 py-2 bg-black/30 border border-green-500/30 rounded text-white placeholder-gray-500"
                  />
                  <input
                    type="file"
                    accept="audio/*"
                    onChange={(e) => setFormData(prev => ({ ...prev, file: e.target.files?.[0] }))}
                    className="px-3 py-2 bg-black/30 border border-green-500/30 rounded text-white"
                  />
                </div>
                <button
                  onClick={handleUploadTrack}
                  className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 rounded transition"
                >
                  Upload Track
                </button>
              </div>
            )}

            {/* Playlist Form */}
            {showPlaylistForm && (
              <div className="mb-6 p-6 bg-green-600/10 border border-green-500/30 rounded-lg space-y-4">
                <h3 className="text-lg font-semibold">Create Playlist</h3>
                <input
                  type="text"
                  placeholder="Playlist Name"
                  value={playlistName}
                  onChange={(e) => setPlaylistName(e.target.value)}
                  className="w-full px-3 py-2 bg-black/30 border border-green-500/30 rounded text-white placeholder-gray-500"
                />
                <button
                  onClick={handleCreatePlaylist}
                  className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 rounded transition"
                >
                  Create
                </button>
              </div>
            )}

            {/* Search */}
            <div className="mb-6 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search tracks, artists..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-black/30 border border-green-500/30 rounded text-white placeholder-gray-500"
              />
            </div>

            {/* Tracks */}
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <Loader2 className="w-8 h-8 animate-spin text-green-400" />
              </div>
            ) : filteredTracks.length === 0 ? (
              <div className="text-center text-gray-400 py-12">
                {tracks.length === 0 ? 'No tracks yet. Upload one to get started!' : 'No tracks match your search.'}
              </div>
            ) : (
              <div className="space-y-2">
                {filteredTracks.map((track) => (
                  <div
                    key={track._id}
                    className="p-4 bg-green-600/10 border border-green-500/30 rounded-lg hover:border-green-500/60 transition cursor-pointer flex items-center justify-between"
                  >
                    <div className="flex-1" onClick={() => handlePlayTrack(track)}>
                      <h4 className="font-semibold text-white">{track.title}</h4>
                      <p className="text-sm text-gray-400">{track.artist}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handlePlayTrack(track);
                        }}
                        className="p-2 bg-green-600 hover:bg-green-700 rounded-full transition"
                      >
                        <PlayIcon className="w-4 h-4" />
                      </button>
                      {playlists.length > 0 && (
                        <select
                          onChange={(e) => handleAddToPlaylist(e.target.value)}
                          className="px-2 py-1 bg-black/30 border border-green-500/30 rounded text-sm text-white"
                        >
                          <option value="">Add to...</option>
                          {playlists.map((p) => (
                            <option key={p._id} value={p._id}>{p.name}</option>
                          ))}
                        </select>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Player Footer */}
        {currentTrack && (
          <div className="h-24 border-t border-green-500/20 bg-black/80 p-4 flex items-center justify-between gap-4">
            <div className="flex-1">
              <p className="text-white font-semibold">{currentTrack.title}</p>
              <p className="text-sm text-gray-400">{currentTrack.artist}</p>
            </div>
            <div className="flex items-center gap-4">
              <button className="p-2 hover:bg-green-500/20 rounded transition">
                <SkipBack className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="p-2 bg-green-600 hover:bg-green-700 rounded transition"
              >
                {isPlaying ? <Loader2 className="w-4 h-4 animate-spin" /> : <PlayIcon className="w-4 h-4" />}
              </button>
              <button className="p-2 hover:bg-green-500/20 rounded transition">
                <SkipForward className="w-4 h-4" />
              </button>
              <Volume className="w-4 h-4 text-gray-400" />
              <input type="range" min="0" max="100" defaultValue="70" className="w-24" />
            </div>
          </div>
        )}
      </div>
    );
  };

  if (location.pathname === "/marketplace") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <div className="h-screen bg-[#050505]">
          <Toaster position="top-center" theme="dark" />
          <MarketplaceBuilder />
        </div>
      </>
    );
  }

  if (location.pathname === "/ads") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <div className="h-screen bg-[#050505]">
          <Toaster position="top-center" theme="dark" />
          <AdsBuilder />
        </div>
      </>
    );
  }

  if (location.pathname === "/socials") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <div className="h-screen bg-[#050505]">
          <Toaster position="top-center" theme="dark" />
          <SocialMediaBuilder navigate={navigate} user={user} showAuth={() => setShowAuth(true)} showPro={() => setShowPro(true)} showProfile={() => setShowProfile(true)} logout={logout} />
        </div>
      </>
    );
  }

  if (location.pathname === "/image-resizer") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <div className="h-screen bg-[#050505]">
          <Toaster position="top-center" theme="dark" />
          <ImageResizerBuilder />
        </div>
      </>
    );
  }

  if (location.pathname === "/image-converter") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <div className="h-screen bg-[#050505]">
          <Toaster position="top-center" theme="dark" />
          <ImageConverterBuilder />
        </div>
      </>
    );
  }

  if (location.pathname === "/multitube") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <div className="h-screen bg-[#050505]">
          <Toaster position="top-center" theme="dark" />
          <MultiTubeBuilder />
        </div>
      </>
    );
  }

  if (location.pathname === "/music") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <div className="h-screen bg-[#050505]">
          <Toaster position="top-center" theme="dark" />
          <MusicBuilder />
        </div>
      </>
    );
  }

  if (location.pathname === "/ai-filter-studio") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <div className="h-screen bg-[#050505]">
          <Toaster position="top-center" theme="dark" />
          <AIFilterStudio />
        </div>
      </>
    );
  }

  // Modern Dashboards
  if (location.pathname === "/dashboard/subscriptions") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <div className="h-screen bg-[#050505]">
          <Toaster position="top-center" theme="dark" />
          <ModernCreatorDashboard />
        </div>
      </>
    );
  }

  if (location.pathname === "/dashboard/ecommerce") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <div className="h-screen bg-[#050505]">
          <Toaster position="top-center" theme="dark" />
          <ModernECommerceDashboard />
        </div>
      </>
    );
  }

  if (location.pathname === "/dashboard/duet") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <div className="h-screen bg-[#050505]">
          <Toaster position="top-center" theme="dark" />
          <ModernDuetCollabDashboard />
        </div>
      </>
    );
  }

  if (location.pathname === "/image-editor") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <div className="h-screen bg-[#050505]">
          <Toaster position="top-center" theme="dark" />
          <ImageEditorAdvanced />
        </div>
      </>
    );
  }

  if (location.pathname === "/newsletter") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <div className="h-screen bg-[#050505]">
          <Toaster position="top-center" theme="dark" />
          <NewsletterDashboard />
        </div>
      </>
    );
  }

  if (location.pathname === "/qrcode") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <div className="h-screen bg-[#050505]">
          <Toaster position="top-center" theme="dark" />
          <QRCodeDashboard />
        </div>
      </>
    );
  }

  if (location.pathname === "/ai-canvas") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <Toaster position="top-center" theme="dark" />
        <AICanvasEnhanced />
      </>
    );
  }

  if (location.pathname === "/ai-tutoring") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <Toaster position="top-center" theme="dark" />
        <AITutoringPlatform />
      </>
    );
  }

  if (location.pathname === "/adaptive-elearning") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <Toaster position="top-center" theme="dark" />
        <AdaptiveELearningPage />
      </>
    );
  }

  if (location.pathname === "/peer-learning") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <Toaster position="top-center" theme="dark" />
        <PeerLearningPage />
      </>
    );
  }

  if (location.pathname === "/content-generation") {
    return (
      <>
        <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
        <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
        <Toaster position="top-center" theme="dark" />
        <ContentGenerationPage />
      </>
    );
  }

  // Auto-name session based on first message
  const autoNameSession = async (sessionId, message) => {
    const name = message.slice(0, 30) + (message.length > 30 ? "..." : "");
    try {
      await api.put(`/sessions/${sessionId}`, { name });
      setSessions(prev => prev.map(s => s.id === sessionId ? { ...s, name } : s));
    } catch (error) {}
  };

  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (!input.trim() || loading) return;
    const userInput = input.trim();
    setInput("");
    setLoading(true);

    try {
      if (mode === "chat") {
        let sessionId = currentSession?.id;
        let isNewSession = false;
        if (!sessionId) {
          const res = await api.post("/sessions?name=New Chat");
          sessionId = res.data.id;
          setCurrentSession(res.data);
          setSessions(prev => [res.data, ...prev]);
          isNewSession = true;
        }
        const tempUserMsg = { id: `temp-${Date.now()}`, role: "user", content: userInput, timestamp: new Date().toISOString() };
        setMessages(prev => [...prev, tempUserMsg]);
        
        // Auto-name session on first message
        if (isNewSession || (messages.length === 0)) {
          autoNameSession(sessionId, userInput);
        }
        
        const res = await api.post("/chat", { session_id: sessionId, message: userInput });
        setMessages(prev => {
          const filtered = prev.filter(m => m.id !== tempUserMsg.id);
          return [...filtered, { ...tempUserMsg, id: `user-${Date.now()}` }, { id: res.data.id, role: "assistant", content: res.data.content, timestamp: res.data.timestamp }];
        });
      } else if (mode === "image") {
        trackGeneration(); // Track for ads
        const toastId = toast.loading("Generating image...");
        // Run image generation in background (non-blocking)
        api.post("/image/generate", { prompt: userInput, session_id: currentSession?.id }, { timeout: 300000 })
          .then(res => {
            const newGen = { ...res.data, type: "image", url: res.data.image_url || res.data.url };
            setGenerations(prev => [newGen, ...prev]);
            toast.dismiss(toastId);
            toast.success("Image generated!");
          })
          .catch(() => {
            toast.dismiss(toastId);
            toast.error("Image generation failed");
          });
        setLoading(false);
        return; // Don't wait
      } else if (mode === "video") {
        trackGeneration(); // Track for ads
        const toastId = toast.loading("Generating video...");
        // Run video generation in background (non-blocking)
        api.post("/video/generate", { prompt: userInput, duration: 5, style: videoStyle, session_id: currentSession?.id }, { timeout: 600000 })
          .then(res => {
            const newGen = { ...res.data, type: "video", url: res.data.video_url || res.data.url };
            setGenerations(prev => [newGen, ...prev]);
            toast.dismiss(toastId);
            toast.success("Video generated!");
          })
          .catch(() => {
            toast.dismiss(toastId);
            toast.error("Video generation failed");
          });
        setLoading(false);
        return; // Don't wait
      } else if (mode === "audio") {
        trackGeneration(); // Track for ads
        const toastId = toast.loading("Generating audio...");
        // Run audio generation in background (non-blocking)
        api.post("/audio/generate", { prompt: userInput, duration: 10, type: "music" })
          .then(res => {
            const newGen = { ...res.data, type: "audio", url: res.data.audio_url || res.data.url };
            setGenerations(prev => [newGen, ...prev]);
            toast.dismiss(toastId);
            toast.success("Audio generated!");
          })
          .catch(() => {
            toast.dismiss(toastId);
            toast.error("Audio generation failed");
          });
        setLoading(false);
        return; // Don't wait
      } else if (mode === "file") {
        trackGeneration(); // Track for ads
        const toastId = toast.loading("Generating file...");
        const res = await api.post("/file/generate", { prompt: userInput, file_type: fileType });
        const newGen = { ...res.data, type: "file", url: res.data.file_url || res.data.url };
        setGenerations(prev => [newGen, ...prev]);
        toast.dismiss(toastId);
        toast.success("File generated!");
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const handleSpeak = async (text) => {
    try {
      toast.info("Generating speech...");
      const res = await api.post("/tts", { text, voice: "en" }, { responseType: 'blob' });
      const audioUrl = URL.createObjectURL(res.data);
      new Audio(audioUrl).play();
    } catch (error) {
      toast.error("TTS failed");
    }
  };

  const toggleRecording = async () => {
    if (isRecording) {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];
        mediaRecorder.ondataavailable = (e) => audioChunksRef.current.push(e.data);
        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          stream.getTracks().forEach(track => track.stop());
          toast.info("Transcribing...");
          const formData = new FormData();
          formData.append('audio', audioBlob, 'recording.webm');
          try {
            const res = await api.post("/stt", formData, { headers: { 'Content-Type': 'multipart/form-data' } });
            setInput(res.data.text);
            inputRef.current?.focus();
          } catch (error) {
            toast.error("Transcription failed");
          }
        };
        mediaRecorder.start();
        setIsRecording(true);
      } catch (error) {
        toast.error("Microphone access denied");
      }
    }
  };

  const ModeConfig = MODES[mode];

  return (
    <>
      <AuthModal open={showAuth} onClose={() => setShowAuth(false)} />
      <ProfileModal open={showProfile} onClose={() => setShowProfile(false)} />
      <ProModal open={showPro} onClose={() => setShowPro(false)} />
      <VideoAdModal 
        open={showVideoAd} 
        onClose={() => setShowVideoAd(false)} 
        onUpgrade={() => { setShowVideoAd(false); setShowPro(true); }} 
      />
      
      <div className="h-screen flex bg-[#050505] overflow-hidden">
        <Toaster position="top-center" theme="dark" />
        
        <Sidebar 
          mode={mode} setMode={setMode} sessions={sessions} currentSession={currentSession}
          setCurrentSession={setCurrentSession} setSidebarOpen={setSidebarOpen} sidebarOpen={sidebarOpen}
          createSession={createSession} deleteSession={deleteSession} navigate={navigate}
          user={user} showAuth={() => setShowAuth(true)} showPro={() => setShowPro(true)} 
          showProfile={() => setShowProfile(true)} logout={logout}
        />

        {/* Mobile overlay */}
        {sidebarOpen && <div className="fixed inset-0 bg-black/50 z-40 md:hidden" onClick={() => setSidebarOpen(false)} />}

        {/* Main */}
        <main className="flex-1 flex flex-col min-w-0">
          {/* Header */}
          <header className="h-16 border-b border-white/10 flex items-center justify-between px-4 md:px-6 glass">
            <div className="flex items-center gap-4">
              <button className="md:hidden p-2 hover:bg-white/5 rounded-lg" onClick={() => setSidebarOpen(true)} data-testid="menu-btn">
                <Menu className="w-5 h-5" />
              </button>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${mode === "chat" ? "bg-purple-400" : mode === "image" ? "bg-cyan-400" : mode === "video" ? "bg-orange-400" : mode === "audio" ? "bg-green-400" : "bg-pink-400"} animate-pulse`} />
                <span className="font-secondary text-sm font-semibold uppercase">{MODES[mode].label} Mode</span>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              {mode === "video" && (
                <Select value={videoStyle} onValueChange={setVideoStyle}>
                  <SelectTrigger className="w-28 h-8 bg-white/5 border-white/10 text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="cinematic">Cinematic</SelectItem>
                    <SelectItem value="anime">Anime</SelectItem>
                    <SelectItem value="realistic">Realistic</SelectItem>
                    <SelectItem value="artistic">Artistic</SelectItem>
                  </SelectContent>
                </Select>
              )}
              
              {mode === "file" && (
                <Select value={fileType} onValueChange={setFileType}>
                  <SelectTrigger className="w-28 h-8 bg-white/5 border-white/10 text-xs">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="code">Code</SelectItem>
                    <SelectItem value="document">Document</SelectItem>
                    <SelectItem value="data">JSON/CSV</SelectItem>
                    <SelectItem value="config">Config</SelectItem>
                  </SelectContent>
                </Select>
              )}
              
              {/* New Chat button at top right */}
              {mode === "chat" && (
                <Button size="sm" onClick={createSession} variant="outline" className="h-8 text-xs">
                  <Plus className="w-4 h-4 mr-1" /> New Chat
                </Button>
              )}
            </div>
          </header>

          {/* Content */}
          <div className="flex-1 overflow-hidden flex flex-col">
            {mode === "chat" ? (
              <ScrollArea className="flex-1">
                <div className="max-w-4xl mx-auto p-4 md:p-6 pb-8">
                  {messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center py-20">
                      <div className="w-20 h-20 rounded-2xl bg-primary/20 flex items-center justify-center mb-6">
                        <Sparkles className="w-10 h-10 text-primary" />
                      </div>
                      <h2 className="font-secondary text-2xl font-bold mb-2">Welcome to GAAIUS</h2>
                      <p className="text-muted-foreground max-w-md">Your unified AI assistant. Chat, images, videos, audio, and files.</p>
                    </div>
                  ) : (
                    messages.map(msg => <ChatMessage key={msg.id} message={msg} onSpeak={handleSpeak} />)
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>
            ) : (
              <ScrollArea className="flex-1">
                <div className="max-w-6xl mx-auto p-4 md:p-6 pb-8">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {generations.filter(g => g.type === mode || (mode === "file" && g.type === "file")).map(gen => (
                      <GenerationResult key={gen.id} data={gen} type={gen.type} />
                    ))}
                    {generations.filter(g => g.type === mode || (mode === "file" && g.type === "file")).length === 0 && (
                      <div className="col-span-full text-center py-20">
                        <div className={`w-20 h-20 rounded-2xl ${ModeConfig.bgColor} flex items-center justify-center mb-6 mx-auto`}>
                          <ModeConfig.icon className={`w-10 h-10 ${ModeConfig.color}`} />
                        </div>
                        <h2 className="font-secondary text-xl font-bold mb-2">No {mode}s yet</h2>
                        <p className="text-muted-foreground">Enter a prompt to generate</p>
                      </div>
                    )}
                  </div>
                </div>
              </ScrollArea>
            )}

            {/* Ad Banner - Only for logged-out users */}
            {!user && <AdBanner onUpgrade={() => setShowAuth(true)} />}

            {/* Input - Fixed at bottom with proper spacing */}
            <div className="p-4 glass">
              <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
                <div className={`rounded-2xl p-2 flex items-center gap-2 ${ModeConfig.borderColor} border bg-black/40`}>
                  <button type="button" onClick={toggleRecording} className={`p-3 rounded-xl transition-all ${isRecording ? "bg-red-500/20 text-red-400" : "hover:bg-white/5 text-muted-foreground"}`} data-testid="voice-btn">
                    {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                  </button>
                  <input ref={inputRef} type="text" value={input} onChange={(e) => setInput(e.target.value)}
                    placeholder={mode === "chat" ? "Message GAAIUS..." : mode === "image" ? "Describe the image..." : mode === "video" ? "Describe the video..." : mode === "audio" ? "Describe music/sound..." : "Describe the file to generate..."}
                    className="flex-1 bg-transparent border-none outline-none text-base py-2 px-2" disabled={loading} data-testid="chat-input" />
                  <Button type="submit" disabled={loading || !input.trim()} className={`rounded-xl px-4 ${ModeConfig.bgColor}`} data-testid="send-btn">
                    {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </main>
      </div>
      
      {/* Persistent Media Player */}
      <PersistentMediaPlayer 
        userId={user?.id || 'guest'} 
        onMediaChange={(media) => {
          console.log('Media changed:', media);
        }}
      />
    </>
  );
};

// Sidebar Component
const Sidebar = ({ mode, setMode, sessions, currentSession, setCurrentSession, setSidebarOpen, sidebarOpen, createSession, deleteSession, navigate, user, showAuth, showPro, showProfile, logout }) => {
  return (
    <aside className={`fixed md:relative z-50 h-full w-56 glass border-r border-white/10 flex flex-col transition-transform duration-300 ${sidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}`} data-testid="sidebar">
      {/* Logo - Compact */}
      <div className="px-3 py-3 border-b border-white/10">
        <h1 className="font-secondary text-lg font-bold">GAAIUS</h1>
        <p className="text-[10px] text-muted-foreground -mt-0.5">AI FROM GAAIUS AI</p>
      </div>

      {/* Mode Selector - Reorganized Layout */}
      <div className="px-3 py-2 border-b border-white/10">
        <p className="font-mono text-[10px] text-muted-foreground uppercase mb-2">Modes</p>
        {/* Row 1: Chat + Image */}
        <div className="flex gap-1 mb-1">
          {["chat", "image"].map((key) => {
            const config = MODES[key];
            const Icon = config.icon;
            return (
              <button key={key} onClick={() => setMode(key)} className={`flex-1 p-1.5 rounded-lg transition-all flex items-center justify-center gap-1 ${mode === key ? `${config.bgColor} ${config.borderColor} border` : "hover:bg-white/5"}`} data-testid={`mode-${key}`}>
                <Icon className={`w-3.5 h-3.5 ${mode === key ? config.color : "text-muted-foreground"}`} />
                <span className={`text-[10px] ${mode === key ? config.color : "text-muted-foreground"}`}>{config.label}</span>
              </button>
            );
          })}
        </div>
        {/* Row 2: Video */}
        <div className="flex gap-1 mb-1">
          {["video"].map((key) => {
            const config = MODES[key];
            const Icon = config.icon;
            return (
              <button key={key} onClick={() => setMode(key)} className={`flex-1 p-1.5 rounded-lg transition-all flex items-center justify-center gap-1 ${mode === key ? `${config.bgColor} ${config.borderColor} border` : "hover:bg-white/5"}`} data-testid={`mode-${key}`}>
                <Icon className={`w-3.5 h-3.5 ${mode === key ? config.color : "text-muted-foreground"}`} />
                <span className={`text-[10px] ${mode === key ? config.color : "text-muted-foreground"}`}>{config.label}</span>
              </button>
            );
          })}
        </div>
        {/* Row 3: Audio + File */}
        <div className="flex gap-1">
          {["audio", "file"].map((key) => {
            const config = MODES[key];
            const Icon = config.icon;
            return (
              <button key={key} onClick={() => setMode(key)} className={`flex-1 p-1.5 rounded-lg transition-all flex items-center justify-center gap-1 ${mode === key ? `${config.bgColor} ${config.borderColor} border` : "hover:bg-white/5"}`} data-testid={`mode-${key}`}>
                <Icon className={`w-3.5 h-3.5 ${mode === key ? config.color : "text-muted-foreground"}`} />
                <span className={`text-[10px] ${mode === key ? config.color : "text-muted-foreground"}`}>{config.label}</span>
              </button>
            );
          })}
        </div>
        {/* Row 4: Socials */}
        <div className="flex gap-1">
          {["socials"].map((key) => {
            const config = MODES[key];
            const Icon = config.icon;
            return (
              <button key={key} onClick={() => navigate("/socials")} className={`flex-1 p-1.5 rounded-lg transition-all flex items-center justify-center gap-1 hover:bg-white/5 border border-pink-500/30 bg-pink-500/10`} data-testid={`mode-${key}`}>
                <Icon className="w-3.5 h-3.5 text-pink-400" />
                <span className="text-[10px] text-pink-400">Socials</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Navigation - Compact */}
      <div className="px-3 py-2 border-b border-white/10">
        <p className="font-mono text-[10px] text-muted-foreground uppercase mb-1">Tools</p>
        <div className="space-y-0.5">
          <button onClick={() => navigate("/projects")} className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-white/5 text-left">
            <FolderOpen className="w-3.5 h-3.5 text-muted-foreground" /><span className="text-xs">Projects</span>
          </button>
          <button onClick={() => navigate("/build")} className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-white/5 text-left">
            <Hammer className="w-3.5 h-3.5 text-orange-400" /><span className="text-xs">AI Builder</span>
          </button>
          <button onClick={() => navigate("/documents")} className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-white/5 text-left">
            <FileCode className="w-3.5 h-3.5 text-cyan-400" /><span className="text-xs">Document Studio</span>
          </button>
          <button onClick={() => navigate("/socials")} className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-white/5 text-left">
            <Video className="w-3.5 h-3.5 text-pink-400" /><span className="text-xs">Socials</span>
          </button>
        </div>
      </div>

      {/* Dashboards - Modern */}
      <div className="px-3 py-2 border-b border-white/10">
        <p className="font-mono text-[10px] text-muted-foreground uppercase mb-1">Dashboards & Tools</p>
        <div className="space-y-0.5">
          <button onClick={() => navigate("/ai-canvas")} className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-indigo-500/10 text-left border border-indigo-500/20">
            <Wand2 className="w-3.5 h-3.5 text-indigo-400" /><span className="text-xs text-indigo-400">AI Canvas</span>
          </button>
          <button onClick={() => navigate("/dashboard/subscriptions")} className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-pink-500/10 text-left border border-pink-500/20">
            <Crown className="w-3.5 h-3.5 text-pink-400" /><span className="text-xs text-pink-400">Creator</span>
          </button>
          <button onClick={() => navigate("/dashboard/ecommerce")} className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-purple-500/10 text-left border border-purple-500/20">
            <ShoppingCart className="w-3.5 h-3.5 text-purple-400" /><span className="text-xs text-purple-400">Store</span>
          </button>
          <button onClick={() => navigate("/dashboard/duet")} className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-indigo-500/10 text-left border border-indigo-500/20">
            <Video className="w-3.5 h-3.5 text-indigo-400" /><span className="text-xs text-indigo-400">Duet</span>
          </button>
          <button onClick={() => navigate("/image-editor")} className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-rose-500/10 text-left border border-rose-500/20">
            <Wand2 className="w-3.5 h-3.5 text-rose-400" /><span className="text-xs text-rose-400">Image Editor</span>
          </button>
          <button onClick={() => navigate("/newsletter")} className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-cyan-500/10 text-left border border-cyan-500/20">
            <Mail className="w-3.5 h-3.5 text-cyan-400" /><span className="text-xs text-cyan-400">Newsletter</span>
          </button>
          <button onClick={() => navigate("/qrcode")} className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-violet-500/10 text-left border border-violet-500/20">
            <QrCode className="w-3.5 h-3.5 text-violet-400" /><span className="text-xs text-violet-400">QR Code</span>
          </button>
          <button onClick={() => navigate("/filter-studio")} className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-yellow-500/10 text-left border border-yellow-500/20">
            <Zap className="w-3.5 h-3.5 text-yellow-400" /><span className="text-xs text-yellow-400">Filter Studio</span>
          </button>
          <button onClick={() => navigate("/ai-tutoring")} className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-emerald-500/10 text-left border border-emerald-500/20">
            <Brain className="w-3.5 h-3.5 text-emerald-400" /><span className="text-xs text-emerald-400">AI Tutoring</span>
          </button>
          <button onClick={() => navigate("/adaptive-elearning")} className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-blue-500/10 text-left border border-blue-500/20">
            <BookOpen className="w-3.5 h-3.5 text-blue-400" /><span className="text-xs text-blue-400">Adaptive eLearning</span>
          </button>
          <button onClick={() => navigate("/peer-learning")} className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-purple-500/10 text-left border border-purple-500/20">
            <Users className="w-3.5 h-3.5 text-purple-400" /><span className="text-xs text-purple-400">Peer Learning</span>
          </button>
          <button onClick={() => navigate("/content-generation")} className="w-full flex items-center gap-2 p-1.5 rounded-lg hover:bg-cyan-500/10 text-left border border-cyan-500/20">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" /><span className="text-xs text-cyan-400">Content Studio</span>
          </button>
        </div>
      </div>

      {/* Sessions - Compact */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <div className="px-3 py-2 flex items-center justify-between">
          <p className="font-mono text-[10px] text-muted-foreground uppercase">Chats</p>
          <Button size="sm" variant="ghost" onClick={createSession} className="h-5 w-5 p-0" data-testid="new-chat-btn">
            <Plus className="w-3 h-3" />
          </Button>
        </div>
        <ScrollArea className="flex-1 px-3">
          {sessions.map(session => (
            <div key={session.id} className={`group flex items-center gap-2 p-2 rounded-lg mb-1 cursor-pointer transition-all ${currentSession?.id === session.id ? "bg-primary/20 border border-primary/30" : "hover:bg-white/5"}`}
              onClick={() => { 
                setCurrentSession(session); 
                setSidebarOpen(false);
                setMode("chat");
                navigate("/");
              }} data-testid={`session-${session.id}`}>
              <MessageSquare className="w-3 h-3 text-muted-foreground flex-shrink-0" />
              <span className="flex-1 truncate text-xs">{session.name}</span>
              <button onClick={(e) => { e.stopPropagation(); deleteSession(session.id); }} className="opacity-0 group-hover:opacity-100 p-0.5 hover:bg-white/10 rounded flex-shrink-0" data-testid={`delete-session-${session.id}`}>
                <Trash2 className="w-3 h-3 text-destructive" />
              </button>
            </div>
          ))}
        </ScrollArea>
      </div>

      {/* User - Compact */}
      <div className="px-3 py-2 border-t border-white/10">
        {user ? (
          <div className="glass-light rounded-lg p-2">
            <div 
              className="flex items-center gap-2 cursor-pointer hover:opacity-80"
              onClick={showProfile}
            >
              <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center">
                <User className="w-3 h-3 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium truncate">{user.name || user.email}</p>
                {user.is_pro && <span className="text-[10px] text-yellow-400 flex items-center gap-0.5"><Crown className="w-2.5 h-2.5" /> Pro</span>}
              </div>
            </div>
            {!user.is_pro && (
              <Button size="sm" onClick={showPro} className="w-full mt-1.5 bg-yellow-500 hover:bg-yellow-600 text-black text-[10px] h-6">
                <Crown className="w-2.5 h-2.5 mr-1" /> Go Pro
              </Button>
            )}
          </div>
        ) : (
          <Button onClick={showAuth} className="w-full h-7 text-xs" variant="outline">
            <User className="w-3 h-3 mr-1" /> Sign In
          </Button>
        )}
      </div>
    </aside>
  );
};

// App with Router
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/*" element={<MainApp />} />
      </Routes>
      <PWAInstallBanner />
    </BrowserRouter>
  );
}

export default App;
