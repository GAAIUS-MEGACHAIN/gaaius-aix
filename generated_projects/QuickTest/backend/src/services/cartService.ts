import prisma from '../config/database';

class CartserviceService {
  async list() {
    return await prisma.cartservice.findMany();
  }

  async getById(id: string) {
    return await prisma.cartservice.findUnique({
      where: { id },
    });
  }

  async create(data: any) {
    return await prisma.cartservice.create({
      data,
    });
  }

  async update(id: string, data: any) {
    return await prisma.cartservice.update({
      where: { id },
      data,
    });
  }

  async delete(id: string) {
    return await prisma.cartservice.delete({
      where: { id },
    });
  }
}

export default new CartserviceService();

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation

// Service implementation
