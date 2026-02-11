import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Avatar,
  Typography,
  Divider,
  Grid,
  Chip,
  InputAdornment,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Tooltip,
  Badge,
  Menu,
  MenuItem,
  AppBar,
  Toolbar,
  Tabs,
  Tab
} from '@mui/material';
import {
  Send as SendIcon,
  AttachFile as AttachFileIcon,
  Search as SearchIcon,
  MoreVert as MoreVertIcon,
  Block as BlockIcon,
  Delete as DeleteIcon,
  Phone as PhoneIcon,
  VideoCall as VideoCallIcon,
  Info as InfoIcon,
  Add as AddIcon,
  Close as CloseIcon,
  Check as CheckIcon,
  DoneAll as DoneAllIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

// Styled components
const ChatContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  height: 'calc(100vh - 120px)',
  gap: theme.spacing(1),
  padding: theme.spacing(1),
  backgroundColor: '#f5f5f5'
}));

const ConversationList = styled(Paper)(({ theme }) => ({
  width: '25%',
  minWidth: '300px',
  overflowY: 'auto',
  borderRadius: theme.spacing(1)
}));

const ChatWindow = styled(Paper)(({ theme }) => ({
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  borderRadius: theme.spacing(1),
  overflow: 'hidden'
}));

const MessagesArea = styled(Box)(({ theme }) => ({
  flex: 1,
  overflowY: 'auto',
  padding: theme.spacing(2),
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(1),
  backgroundColor: '#ffffff'
}));

const MessageBubble = styled(Paper)(({ theme, isOwn }) => ({
  padding: theme.spacing(1.5, 2),
  maxWidth: '60%',
  alignSelf: isOwn ? 'flex-end' : 'flex-start',
  backgroundColor: isOwn ? theme.palette.primary.main : theme.palette.grey[200],
  color: isOwn ? '#fff' : '#000',
  borderRadius: theme.spacing(2),
  wordWrap: 'break-word'
}));

const InputArea = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  display: 'flex',
  gap: theme.spacing(1),
  borderTop: `1px solid ${theme.palette.divider}`
}));

const ConversationListItem = styled(ListItemButton)(({ theme, selected }) => ({
  backgroundColor: selected ? theme.palette.action.selected : 'transparent',
  '&:hover': {
    backgroundColor: theme.palette.action.hover
  }
}));

// Message Status Icons
const MessageStatusIcon = ({ status }) => {
  if (status === 'sending') return <CircularProgress size={16} />;
  if (status === 'sent') return <CheckIcon sx={{ fontSize: 16 }} />;
  if (status === 'delivered') return <DoneAllIcon sx={{ fontSize: 16 }} />;
  if (status === 'read') return <DoneAllIcon sx={{ fontSize: 16, color: 'primary.main' }} />;
  return null;
};

// Typing Indicator Component
const TypingIndicator = () => (
  <Box sx={{ display: 'flex', gap: 0.5, alignItems: 'center' }}>
    <Box sx={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#999', animation: 'bounce 1.4s infinite' }} />
    <Box sx={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#999', animation: 'bounce 1.4s infinite 0.2s' }} />
    <Box sx={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: '#999', animation: 'bounce 1.4s infinite 0.4s' }} />
  </Box>
);

// Main Component
const MessagingPlatform = () => {
  // State
  const [activeTab, setActiveTab] = useState(0);
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messageInput, setMessageInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [contacts, setContacts] = useState([]);
  const [users, setUsers] = useState([]);
  const [currentUser] = useState(localStorage.getItem('userId') || 'user-' + Math.random().toString(36).substr(2, 9));
  const [typingUsers, setTypingUsers] = useState(new Set());
  const [userPresence, setUserPresence] = useState({});
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [openNewChat, setOpenNewChat] = useState(false);
  const [openGroupChat, setOpenGroupChat] = useState(false);
  const [groupName, setGroupName] = useState('');
  const [selectedMembers, setSelectedMembers] = useState([]);
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize WebSocket
  useEffect(() => {
    const initWebSocket = () => {
      const wsUrl = `ws://localhost:8000/api/v1/messages/ws/${currentUser}`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
      };

      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'new_message') {
          const message = data.data;
          if (selectedConversation?.id === message.conversation_id) {
            setMessages(prev => [...prev, message]);
          }
        } else if (data.type === 'typing') {
          if (data.is_typing) {
            setTypingUsers(prev => new Set([...prev, data.user_id]));
          } else {
            setTypingUsers(prev => {
              const newSet = new Set(prev);
              newSet.delete(data.user_id);
              return newSet;
            });
          }
        } else if (data.type === 'presence_update') {
          setUserPresence(prev => ({
            ...prev,
            [data.user_id]: data.presence
          }));
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    };

    initWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [currentUser, selectedConversation]);

  // Load conversations
  useEffect(() => {
    loadConversations();
    loadContacts();
  }, []);

  const loadConversations = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`/api/v1/messages/conversations/${currentUser}`);
      const data = await response.json();
      setConversations(data.data || []);
      if (data.data && data.data.length > 0) {
        setSelectedConversation(data.data[0]);
        await loadMessages(data.data[0].id);
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadMessages = async (conversationId) => {
    try {
      const response = await fetch(
        `/api/v1/messages/messages/${conversationId}?user_id=${currentUser}&limit=50`
      );
      const data = await response.json();
      setMessages(data.data || []);
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  };

  const loadContacts = async () => {
    try {
      const response = await fetch(`/api/v1/messages/contacts/${currentUser}`);
      const data = await response.json();
      setContacts(data.data || []);
    } catch (error) {
      console.error('Error loading contacts:', error);
    }
  };

  const sendMessage = async () => {
    if (!messageInput.trim() || !selectedConversation) return;

    try {
      const response = await fetch('/api/v1/messages/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          conversation_id: selectedConversation.id,
          sender_id: currentUser,
          content: messageInput,
          message_type: 'text'
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        setMessages(prev => [...prev, data.data]);
        setMessageInput('');
      }
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const startNewChat = async (userId) => {
    try {
      const response = await fetch('/api/v1/messages/conversation/one-to-one', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: currentUser,
          other_user_id: userId
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        await loadConversations();
        setSelectedConversation(data.data);
        await loadMessages(data.data.id);
        setOpenNewChat(false);
      }
    } catch (error) {
      console.error('Error creating conversation:', error);
    }
  };

  const createGroupChat = async () => {
    if (!groupName.trim() || selectedMembers.length === 0) return;

    try {
      const response = await fetch('/api/v1/messages/conversation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          creator_id: currentUser,
          participant_ids: [...selectedMembers, currentUser],
          name: groupName,
          is_group: true
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        await loadConversations();
        setGroupName('');
        setSelectedMembers([]);
        setOpenGroupChat(false);
      }
    } catch (error) {
      console.error('Error creating group:', error);
    }
  };

  const deleteMessage = async (messageId) => {
    try {
      await fetch(`/api/v1/messages/message/${messageId}?user_id=${currentUser}`, {
        method: 'DELETE'
      });
      setMessages(prev => prev.filter(m => m.id !== messageId));
    } catch (error) {
      console.error('Error deleting message:', error);
    }
  };

  const blockUser = async (userId) => {
    try {
      await fetch('/api/v1/messages/user/block', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: currentUser,
          blocked_user_id: userId
        })
      });
      alert('User blocked');
    } catch (error) {
      console.error('Error blocking user:', error);
    }
  };

  const getConversationName = (conversation) => {
    if (conversation.name) return conversation.name;
    const otherUser = conversation.participant_ids.find(id => id !== currentUser);
    return contacts.find(c => c.id === otherUser)?.name || otherUser || 'Unknown';
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ width: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <Typography variant="h6" sx={{ flex: 1 }}>
            💬 Messages
          </Typography>
          <Tooltip title="New Chat">
            <IconButton color="inherit" onClick={() => setOpenNewChat(true)}>
              <AddIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="New Group">
            <IconButton color="inherit" onClick={() => setOpenGroupChat(true)}>
              <AddIcon />
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      {/* Tabs */}
      <Tabs value={activeTab} onChange={handleTabChange} sx={{ backgroundColor: '#f5f5f5' }}>
        <Tab label="Chats" />
        <Tab label="Contacts" />
        <Tab label="Settings" />
      </Tabs>

      {/* Main Content */}
      {activeTab === 0 ? (
        <ChatContainer>
          {/* Conversations List */}
          <ConversationList>
            {/* Search */}
            <Box sx={{ p: 1 }}>
              <TextField
                fullWidth
                size="small"
                placeholder="Search conversations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  )
                }}
              />
            </Box>
            <Divider />

            {/* Conversations */}
            <List sx={{ p: 0 }}>
              {isLoading ? (
                <Box sx={{ p: 2, display: 'flex', justifyContent: 'center' }}>
                  <CircularProgress />
                </Box>
              ) : conversations.length === 0 ? (
                <Box sx={{ p: 2, textAlign: 'center', color: '#999' }}>
                  <Typography>No conversations yet</Typography>
                </Box>
              ) : (
                conversations.map(conv => (
                  <ConversationListItem
                    key={conv.id}
                    selected={selectedConversation?.id === conv.id}
                    onClick={() => {
                      setSelectedConversation(conv);
                      loadMessages(conv.id);
                    }}
                  >
                    <Badge
                      overlap="circular"
                      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                      variant="dot"
                      invisible={userPresence[conv.participant_ids.find(id => id !== currentUser)] !== 'online'}
                      sx={{ mr: 1 }}
                    >
                      <Avatar sx={{ width: 40, height: 40 }}>
                        {getConversationName(conv).charAt(0).toUpperCase()}
                      </Avatar>
                    </Badge>
                    <ListItemText
                      primary={getConversationName(conv)}
                      secondary={conv.last_message_text || 'No messages'}
                      secondaryTypographyProps={{ noWrap: true }}
                    />
                  </ConversationListItem>
                ))
              )}
            </List>
          </ConversationList>

          {/* Chat Window */}
          {selectedConversation ? (
            <ChatWindow>
              {/* Chat Header */}
              <Box sx={{
                p: 2,
                backgroundColor: '#f5f5f5',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderBottom: '1px solid #eee'
              }}>
                <Box>
                  <Typography variant="h6">{getConversationName(selectedConversation)}</Typography>
                  <Typography variant="caption" sx={{ color: '#666' }}>
                    {userPresence[selectedConversation.participant_ids.find(id => id !== currentUser)] === 'online' ? '🟢 Online' : '🔘 Offline'}
                  </Typography>
                </Box>
                <Box>
                  <IconButton size="small"><PhoneIcon /></IconButton>
                  <IconButton size="small"><VideoCallIcon /></IconButton>
                  <IconButton size="small"><InfoIcon /></IconButton>
                </Box>
              </Box>

              {/* Messages */}
              <MessagesArea>
                {messages.map(msg => (
                  <Box
                    key={msg.id}
                    sx={{
                      display: 'flex',
                      justifyContent: msg.sender_id === currentUser ? 'flex-end' : 'flex-start',
                      alignItems: 'flex-end',
                      gap: 1
                    }}
                  >
                    {msg.sender_id !== currentUser && (
                      <Avatar sx={{ width: 32, height: 32 }}>
                        {msg.sender_id.charAt(0).toUpperCase()}
                      </Avatar>
                    )}
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                      <MessageBubble isOwn={msg.sender_id === currentUser}>
                        {msg.message_type === 'file' ? (
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <AttachFileIcon />
                            <a href={msg.file_url} target="_blank" rel="noopener noreferrer">
                              {msg.file_name}
                            </a>
                          </Box>
                        ) : (
                          msg.content
                        )}
                      </MessageBubble>
                      {msg.sender_id === currentUser && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, ml: 2 }}>
                          <MessageStatusIcon status={msg.status} />
                          <Typography variant="caption" sx={{ color: '#999' }}>
                            {new Date(msg.created_at).toLocaleTimeString()}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  </Box>
                ))}
                {typingUsers.size > 0 && (
                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
                    <Avatar sx={{ width: 32, height: 32 }}>?</Avatar>
                    <TypingIndicator />
                  </Box>
                )}
                <div ref={messagesEndRef} />
              </MessagesArea>

              {/* Input Area */}
              <InputArea>
                <IconButton size="small" color="primary">
                  <AttachFileIcon />
                </IconButton>
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Type a message..."
                  value={messageInput}
                  onChange={(e) => setMessageInput(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                  multiline
                  maxRows={3}
                />
                <Tooltip title="Send">
                  <span>
                    <IconButton
                      color="primary"
                      onClick={sendMessage}
                      disabled={!messageInput.trim()}
                    >
                      <SendIcon />
                    </IconButton>
                  </span>
                </Tooltip>
              </InputArea>
            </ChatWindow>
          ) : (
            <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Typography color="textSecondary">Select a conversation to start chatting</Typography>
            </Box>
          )}
        </ChatContainer>
      ) : activeTab === 1 ? (
        // Contacts Tab
        <Box sx={{ p: 2 }}>
          <Grid container spacing={2}>
            {contacts.map(contact => (
              <Grid item xs={12} sm={6} md={4} key={contact.id}>
                <Paper sx={{ p: 2, cursor: 'pointer', '&:hover': { boxShadow: 3 } }}
                       onClick={() => startNewChat(contact.id)}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Badge
                      overlap="circular"
                      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                      variant="dot"
                      invisible={contact.presence !== 'online'}
                    >
                      <Avatar src={contact.avatar}>{contact.name.charAt(0)}</Avatar>
                    </Badge>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle2">{contact.name}</Typography>
                      <Typography variant="caption" sx={{ color: '#999' }}>
                        {contact.presence === 'online' ? '🟢 Online' : '🔘 Offline'}
                      </Typography>
                      {contact.bio && (
                        <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                          {contact.bio}
                        </Typography>
                      )}
                    </Box>
                  </Box>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Box>
      ) : (
        // Settings Tab
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Settings</Typography>
          <Box sx={{ mt: 2 }}>
            <Button variant="contained" color="primary" fullWidth sx={{ mb: 1 }}>
              Notification Settings
            </Button>
            <Button variant="contained" color="primary" fullWidth sx={{ mb: 1 }}>
              Privacy Settings
            </Button>
            <Button variant="contained" color="primary" fullWidth>
              Account Settings
            </Button>
          </Box>
        </Box>
      )}

      {/* New Chat Dialog */}
      <Dialog open={openNewChat} onClose={() => setOpenNewChat(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Start New Chat</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            {contacts.map(contact => (
              <Paper key={contact.id} sx={{ p: 1.5, mb: 1, cursor: 'pointer', '&:hover': { backgroundColor: '#f5f5f5' } }}
                     onClick={() => {
                       startNewChat(contact.id);
                     }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Avatar src={contact.avatar}>{contact.name.charAt(0)}</Avatar>
                  <Typography>{contact.name}</Typography>
                </Box>
              </Paper>
            ))}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenNewChat(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>

      {/* Group Chat Dialog */}
      <Dialog open={openGroupChat} onClose={() => setOpenGroupChat(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create Group Chat</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              fullWidth
              label="Group Name"
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
            />
            <Typography variant="subtitle2">Select Members:</Typography>
            {contacts.map(contact => (
              <Box
                key={contact.id}
                sx={{
                  p: 1,
                  border: '1px solid #eee',
                  borderRadius: 1,
                  cursor: 'pointer',
                  backgroundColor: selectedMembers.includes(contact.id) ? '#e3f2fd' : '#fff'
                }}
                onClick={() => {
                  setSelectedMembers(prev =>
                    prev.includes(contact.id)
                      ? prev.filter(id => id !== contact.id)
                      : [...prev, contact.id]
                  );
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {selectedMembers.includes(contact.id) && <CheckIcon />}
                  <Avatar src={contact.avatar} sx={{ width: 32, height: 32 }}>
                    {contact.name.charAt(0)}
                  </Avatar>
                  <Typography variant="body2">{contact.name}</Typography>
                </Box>
              </Box>
            ))}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenGroupChat(false)}>Cancel</Button>
          <Button
            onClick={createGroupChat}
            variant="contained"
            disabled={!groupName.trim() || selectedMembers.length === 0}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      <style>
        {`
          @keyframes bounce {
            0%, 80%, 100% {
              transform: scaleY(1);
            }
            40% {
              transform: scaleY(0.5);
            }
          }
        `}
      </style>
    </Box>
  );
};

export default MessagingPlatform;
