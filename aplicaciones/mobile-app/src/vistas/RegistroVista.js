import React, { useState } from 'react';
import { ScrollView, TextInput, Button, StyleSheet, Text, Alert } from 'react-native';
import { BASE_URL, API_HEADERS } from '../api/api';

export default function RegistroVista({ navigation }) {
  const [form, setForm] = useState({
    nombre_usuario: '', contraseña: '', nombre: '',
    apellidos: '', dni: '', telefono: '', email: ''
  });

  const handleRegistro = async () => {
    try {
      const response = await fetch(`${BASE_URL}/auth/registro`, {
        method: 'POST',
        headers: API_HEADERS,
        body: JSON.stringify(form),
      });

      const data = await response.json();

      if (response.ok) {
        Alert.alert("Registro satisfactorio", "\nTe has registrado correctamente en la aplicación.\nSerás reenviado al login.");
        navigation.navigate('Login');

      } else {
        Alert.alert("Error", data.ERROR || "Fallo al registrar");
      }
    } catch (e) {
      Alert.alert("Error", "Error de red");
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      {Object.keys(form).map((key) => (
        <TextInput
          key={key}
          placeholder={key.toUpperCase().replace('_', ' ')}
          style={styles.input}
          secureTextEntry={key === 'contraseña'}
          onChangeText={(val) => setForm({ ...form, [key]: val })}
        />
      ))}
      <Button title="Confirmar Registro" onPress={handleRegistro} color="#2ecc71" />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 25 },
  input: { backgroundColor: '#fff', padding: 12, borderRadius: 8, marginBottom: 10, borderWidth: 1, borderColor: '#ddd' }
});