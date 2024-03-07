<template>
  <form @submit.prevent="submitForm">
    <label for="name">Name:</label>
    <input v-model="student.name" type="text" id="name" required>

    <label for="age">Age:</label>
    <input v-model="student.age" type="number" id="age" required>

    <label for="email">Email:</label>
    <input v-model="student.email" type="email" id="email" required>

    <button type="submit">Register</button>
  </form>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import axios from 'axios';

export default defineComponent({
  data() {
    return {
      student: {
        name: '',
        age: 0,
        email: '',
      },
    };
  },
  methods: {
    async submitForm() {
      try {
        const response = await axios.post('/api/register-student/', this.student);
        console.log('Student registered:', response.data);
      } catch (error) {
        console.error('Error registering student:', error);
      }
    },
  },
});
</script>