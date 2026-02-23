import React, { useState } from 'react';
import { View, TextInput, Button, StyleSheet, Text, Alert } from 'react-native';
import { BASE_URL, API_HEADERS } from '../api/api';

export default function LoginVista({ navigation }) {
  const [user, setUser] = useState('');
  const [pass, setPass] = useState('');

  const handleLogin = async () => {
    try {
      const response = await fetch(`${BASE_URL}/auth/login`, {
        method: 'POST',
        headers: API_HEADERS,
        body: JSON.stringify({ nombre_usuario: user, contraseña: pass }),
      });
      const data = await response.json();

      if (response.ok) {
        navigation.replace('Main', { usuario: data.usuario });

      } else {
        Alert.alert("Error", data.ERROR || "Credenciales incorrectas");
      }
    } catch (e) {
      Alert.alert("Error", "No se pudo conectar con el servidor");
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.titulo}>GYM EX</Text>
      <TextInput placeholder="Usuario" style={styles.input} onChangeText={setUser} />
      <TextInput placeholder="Contraseña" secureTextEntry style={styles.input} onChangeText={setPass} />
      <Button title="Entrar" onPress={handleLogin} color="#4f46e5" />
      <Text style={styles.link} onPress={() => navigation.navigate('Registro')}>
        ¿No tienes cuenta? Regístrate aquí
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 30 },
  titulo: { fontSize: 32, fontWeight: 'bold', textAlign: 'center', marginBottom: 40, color: '#4f46e5' },
  input: { backgroundColor: '#fff', padding: 15, borderRadius: 8, marginBottom: 15, borderWidth: 1, borderColor: '#ddd' },
  link: { marginTop: 20, textAlign: 'center', color: '#3498db' }
});