import 'package:flutter/material.dart';
import 'package:shewear/features/screens/message/chatlayout.dart';

class UserChat extends StatefulWidget {
  const UserChat({super.key});

  @override
  _UserChatState createState() => _UserChatState();
}

class _UserChatState extends State<UserChat> {
  // A list of contacts you can chat with
  List<Map<String, String>> contacts = [
    {
      "name": "User 1",
      "lastMessage": "Hello! How are you?",
      "time": "10:30 AM",
      "image": "assets/user1.png",
    },
    {
      "name": "User 2",
      "lastMessage": "I'm doing great, thanks! How about you?",
      "time": "9:45 AM",
      "image": "assets/user2.png",
    },
    {
      "name": "User 3",
      "lastMessage": "I'm good, just wanted to check in.",
      "time": "Yesterday",
      "image": "assets/user3.png",
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("User Chat"),
        foregroundColor: Colors.white,
      ),
      body: ListView.builder(
        itemCount: contacts.length,
        itemBuilder: (context, index) {
          final contact = contacts[index];
          return GestureDetector(
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => ChatLayout(
                    chatPartner: contact["name"] ?? "Unknown",
                  ),
                ),
              );
            },
            child: ListTile(
              contentPadding:
                  const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              leading: CircleAvatar(
                radius: 25,
                backgroundImage:
                    AssetImage(contact["image"] ?? "assets/default_image.png"),
              ),
              title: Text(
                contact["name"] ?? "Unknown",
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Row(
                children: [
                  Expanded(
                    child: Text(
                      contact["lastMessage"] ?? "No message",
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(color: Colors.black54),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    contact["time"] ?? "N/A",
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
