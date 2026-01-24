import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';

class ProductsService {
  private baseURL = `${API_BASE_URL}/products`;

  async fetch(params?: any) {
    try {
      const response = await axios.get(this.baseURL, { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async create(data: any) {
    try {
      const response = await axios.post(this.baseURL, data);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async update(id: string, data: any) {
    try {
      const response = await axios.put(`${this.baseURL}/${id}`, data);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async delete(id: string) {
    try {
      await axios.delete(`${this.baseURL}/${id}`);
    } catch (error) {
      throw error;
    }
  }
}

export default new ProductsService();

// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation
// Service implementation