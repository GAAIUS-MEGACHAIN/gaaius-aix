import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function seed() {
  // Create teams
  const team1 = await prisma.team.create({
    data: {
      name: 'Team 1',
      description: 'This is team 1',
    },
  });

  const team2 = await prisma.team.create({
    data: {
      name: 'Team 2',
      description: 'This is team 2',
    },
  });

  // Create users
  const user1 = await prisma.user.create({
    data: {
      email: 'user1@example.com',
      username: 'user1',
      passwordHash: 'password',
      role: 'USER',
      teamId: team1.id,
    },
  });

  const user2 = await prisma.user.create({
    data: {
      email: 'user2@example.com',
      username: 'user2',
      passwordHash: 'password',
      role: 'USER',
      teamId: team1.id,
    },
  });

  const user3 = await prisma.user.create({
    data: {
      email: 'user3@example.com',
      username: 'user3',
      passwordHash: 'password',
      role: 'USER',
      teamId: team2.id,
    },
  });

  // Create tasks
  const task1 = await prisma.task.create({
    data: {
      title: 'Task 1',
      description: 'This is task 1',
      dueDate: new Date('2024-03-01'),
      status: 'OPEN',
      userId: user1.id,
      teamId: team1.id,
    },
  });

  const task2 = await prisma.task.create({
    data: {
      title: 'Task 2',
      description: 'This is task 2',
      dueDate: new Date('2024-03-02'),
      status: 'OPEN',
      userId: user2.id,
      teamId: team1.id,
    },
  });

  const task3 = await prisma.task.create({
    data: {
      title: 'Task 3',
      description: 'This is task 3',
      dueDate: new Date('2024-03-03'),
      status: 'OPEN',
      userId: user3.id,
      teamId: team2.id,
    },
  });

  // Create comments
  const comment1 = await prisma.comment.create({
    data: {
      text: 'This is comment 1',
      taskId: task1.id,
      userId: user1.id,
    },
  });

  const comment2 = await prisma.comment.create({
    data: {
      text: 'This is comment 2',
      taskId: task2.id,
      userId: user2.id,
    },
  });

  const comment3 = await prisma.comment.create({
    data: {
      text: 'This is comment 3',
      taskId: task3.id,
      userId: user3.id,
    },
  });

  // Create likes
  const like1 = await prisma.like.create({
    data: {
      taskId: task1.id,
      userId: user2.id,
    },
  });

  const like2 = await prisma.like.create({
    data: {
      taskId: task2.id,
      userId: user3.id,
    },
  });

  const like3 = await prisma.like.create({
    data: {
      taskId: task3.id,
      userId: user1.id,
    },
  });

  // Create files
  const file1 = await prisma.file.create({
    data: {
      name: 'file1.txt',
      type: 'text/plain',
      size: 1024,
      taskId: task1.id,
      userId: user1.id,
    },
  });

  const file2 = await prisma.file.create({
    data: {
      name: 'file2.txt',
      type: 'text/plain',
      size: 2048,
      taskId: task2.id,
      userId: user2.id,
    },
  });

  const file3 = await prisma.file.create({
    data: {
      name: 'file3.txt',
      type: 'text/plain',
      size: 4096,
      taskId: task3.id,
      userId: user3.id,
    },
  });
}

seed()
  .catch((e) => console.error(e))
  .finally(async () => {
    await prisma.$disconnect();
  });
```

This schema includes the following entities:

*   **Team**: Represents a team with a unique name and description.
*   **User**: Represents a user with an email, username, password hash, and role.
*   **Task**: Represents a task with a title, description, due date, status, and assigned user and team.
*   **Comment**: Represents a comment on a task with text and associated user and task.
*   **Like**: Represents a like on a task with associated user and task.
*   **File**: Represents a file attached to a task with name, type, size, and associated user and task.

The seed data creates sample teams, users, tasks, comments, likes, and files to populate the database.