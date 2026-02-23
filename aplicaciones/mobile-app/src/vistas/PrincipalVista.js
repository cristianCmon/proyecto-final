import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { BASE_URL, API_HEADERS } from '../api/api';

export default function PrincipalVista({ route }) {
  const { usuario } = route.params;
  const [sesiones, setSesiones] = useState([]);

  const cargarDatos = async () => {
    try {
      const res = await fetch(`${BASE_URL}/sesiones`);
      const data = await res.json();
      setSesiones(data);
      
    } catch (e) { console.log(e); }
  };

  useEffect(() => { cargarDatos(); }, []);

  const reservar = async (idSesion) => {
    try {
      const res = await fetch(`${BASE_URL}/reservas`, {
        method: 'POST',
        headers: API_HEADERS,
        body: JSON.stringify({ id_usuario: usuario.id, id_sesion: idSesion }),
      });

      const data = await res.json();
      
      if (res.ok) {
        Alert.alert("¡Reservado!", "\nNos vemos en clase.");
        cargarDatos();

      } else {
        Alert.alert("Aviso", data.ERROR);
      }

    } catch (e) { Alert.alert("Error", "No se pudo conectar"); }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.welcome}>Hola, {usuario.nombre_usuario}</Text>
      <FlatList
        data={sesiones}
        keyExtractor={item => item.id}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.title}>{item.nombre}</Text>
            <Text>{item.hora_inicio} - {item.hora_fin}</Text>
            <Text>Libres: {item.capacidad_maxima - item.capacidad_actual}</Text>
            <TouchableOpacity 
              style={[styles.btn, item.capacidad_actual >= item.capacidad_maxima && {backgroundColor: '#ccc'}]}
              onPress={() => reservar(item.id)}
              disabled={item.capacidad_actual >= item.capacidad_maxima}
            >
              <Text style={{color: '#fff', fontWeight: 'bold'}}>RESERVAR</Text>
            </TouchableOpacity>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 15, backgroundColor: '#f0f0f0' },
  welcome: { fontSize: 18, marginBottom: 15, fontWeight: 'bold' },
  card: { backgroundColor: '#fff', padding: 20, borderRadius: 12, marginBottom: 15, elevation: 2 },
  title: { fontSize: 20, fontWeight: 'bold', color: '#2c3e50' },
  btn: { backgroundColor: '#3498db', padding: 12, borderRadius: 6, marginTop: 10, alignItems: 'center' }
});